import copy
import sys
import pprint
import os, os.path as op
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from collections import OrderedDict
from functools import partial
from typing import List, Dict
from urllib.parse import urlparse

import yaml
from natsort import natsorted, ns
from pykwalify.core import Core
from slugify import slugify


@dataclass
class Game:
    item: Dict
    meta: Dict
    clones: List

    @property
    def names(self) -> List[str]:
        return names(self.item)

    @property
    def slug(self) -> str:
        return slugify(self.names[0])

    @property
    def wikilink(self) -> str:
        try:
            return "https://en.wikipedia.org/wiki/" + self.meta['external']['wikipedia']
        except KeyError:
            return self.meta['external']['website']


def abort(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def validate(item, key):
    for name in names(item):
        if not (isinstance(name, str) or
                (len(name) == 2 and
                 all(isinstance(x, str) for x in name))):
            abort('Error: %r should be a string or a list of two strings' % name)
    games = item[key]
    if (not isinstance(games, list) or
        not all(isinstance(x, dict) for x in games)):
        print('Error: this should be a list of dicts:')
        abort(pprint.pformat(games))
    return names, games


def names(item):
    return [item['name']] + item.get('names', [])


def game_name(game):
    return game['name'][0] if isinstance(game['name'], list) else game['name']


def parse_tag(tag):
    return tag.replace(' ', '-').lower()


def parse_unicode(text):
    if isinstance(text, str):
        return text
    if isinstance(text, (list, tuple)):
        result = []
        for item in text:
            result.append(parse_unicode(item))
        return result


def parse_unicode_tag(tag):
    return parse_tag(parse_unicode(tag))


def parse_tags(entry, keys):
    tags = []

    for key in keys:
        if key in entry:
            val = entry.get(key)

            if isinstance(val, str):
                tags.append(parse_tag(val))
                tags.append(parse_unicode_tag(val))
            elif isinstance(val, list):
                tags += [parse_tag(v) for v in val]
                tags += [parse_unicode_tag(v) for v in val]
            else:
                abort('Error: %s\'s key "%s" is not valid (%s)' %
                    (entry['name'], key, type(val).__name__))

    result = []
    for tag in tags:
        if tag not in result:
            result.append(tag)

    return result


def parse_global_tags(site, item, tag, item_key: str):
    if tag in item:
        if not getattr(site, tag, False):
            setattr(site, tag, {})

        if isinstance(item[tag], str):
            item[tag] = [item[tag]]

        for t in item[tag]:
            tagObj = getattr(site, tag, False)
            if not tagObj.get(t, False):
                tagObj[t] = {'tag_count': 0, 'keys': set()}
            if item_key not in tagObj[t]['keys']:
                tagObj[t]['tag_count'] += 1
                tagObj[t]['keys'].add(item_key)

    setattr(site, tag, OrderedDict(sorted(getattr(site, tag, {}).items())))


def parse_item(entry, entry_tags=[], meta={}, meta_tags=[]):
    updated = entry.get('updated')
    if isinstance(updated, str):
        updated = datetime.strptime(updated, "%Y-%m-%d").date()
    added = entry.get('added') or date.min
    if isinstance(added, str):
        added = datetime.strptime(added, "%Y-%m-%d").date()
    result = dict(entry,
                  new=added == updated and (date.today() - added) < timedelta(days=30),
                  is_updated=(date.today() - updated) < timedelta(days=30),
                  tags=parse_tags(entry, entry_tags) + parse_tags(meta, meta_tags),
                  updated=updated)

    if "repo" in result:
        # Try to add extra repo information, like icons, badges
        repo_parsed = urlparse(result["repo"])
        domain = repo_parsed.netloc
        ext = os.path.splitext(result["repo"])[1]

        if domain == "github.com":
            try:
                # https://github.com/<user>/<repo>
                _, user, repo, *_ = repo_parsed.path.split("/")
            except ValueError:
                result["repoiconname"] = "github"
                result["repoiconstyle"] = "fab"
                result["repotitle"] = "GitHub"
            else:
                result["repobadge"] = f'<img class="badge lazyload" alt="GitHub stars" data-src="https://img.shields.io/github/stars/{user}/{repo}?style=flat-square&logo=github" src="https://img.shields.io/badge/stars-%3F-blue?style=flat-square&logo=github">'
        elif domain == "code.google.com":
            result["repoiconname"] = "google"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "Google Code"
        elif domain == "bitbucket.org":
            result["repoiconname"] = "bitbucket"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "Bitbucket"
        elif domain == "gitlab.com":
            try:
                # https://gitlab.com/<user>/<repo>
                _, user, repo, *_ = repo_parsed.path.split("/")
            except ValueError:
                result["repoiconname"] = "gitlab"
                result["repoiconstyle"] = "fab"
                result["repotitle"] = "GitLab"
            else:
                result["repobadge"] = f'<img class="badge lazyload" alt="GitLab stars" src="https://img.shields.io/badge/dynamic/json?color=green&label=stars&logo=gitlab&&query=%24.star_count&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2F{user}%252F{repo}">'
        elif domain == "sourceforge.net":
            try:
                # https://sourceforge.net/projects/<repo>
                _, _, repo, *_ = repo_parsed.path.split("/")
            except ValueError:
                pass
            else:
                result["repobadge"] = f'<img class="badge lazyload" alt="Sourceforge downloads" data-src="https://img.shields.io/sourceforge/dt/{repo}?style=flat-square&logo=sourceforge" src="https://img.shields.io/badge/downloads-%3F-brightgreen?style=flat-square&logo=sourceforge">'
        elif ext in (".gz", ".zip", ".tar", ".tgz", ".tbz2", ".bz2", ".xz", ".rar"):
            result["repoiconname"] = "box"
            result["repoiconstyle"] = "fas"
            result["repotitle"] = "Archive"

    return result


def parse_items(site, item, key):
    if not (item.get(key) and validate(item, key)):
        return
    if not getattr(site, key, False):
        setattr(site, key, [])

    meta_tags = ['genres', 'subgenres', 'themes']
    game_tags = [
        'status',
        'development',
        'langs',
        'frameworks',
        'content',
        'licenses',
        'multiplayer',
        'type'
    ]

    meta = item.get('meta', {})
    meta["names_ascii"] = parse_unicode(names(item))
    meta["external"] = item.get('external', {})
    parse_global_tags(site, meta, 'genres', item['name'])
    parse_global_tags(site, meta, 'subgenres', item['name'])
    parse_global_tags(site, meta, 'themes', item['name'])

    parse_fn = partial(parse_item, entry_tags=game_tags, meta=meta, meta_tags=meta_tags)

    for game in item[key]:
        parse_global_tags(site, game, 'langs', game['name'])

    getattr(site, key).append(Game(item, meta, [parse_fn(i) for i in item[key]]))


def show_error(game_name, error_str):
    print(f'\033[91m  {game_name}\033[0m')
    print(f'    {error_str}')


def show_errors(errors):
    print('\n')
    for error in errors:
        show_error(error["name"], error["error"])
    print(f'\n  {len(errors)} errors\n')
    sys.exit(1)


def show_validation_errors(data, validation_errors):
    errors = []
    for error in validation_errors:
        path = error.path.split('/')
        game = data[int(path[1])]
        name = game_name(game)

        errors.append({"name": name, "error": error.__repr__()})

    show_errors(errors)


def validate_with_schema(source_data, schema_file):
    core = Core(source_data=source_data, schema_files=[schema_file])
    try:
        core.validate(raise_exception=True)
    except Exception as error:
        if len(core.errors) > 0:
            show_validation_errors(source_data, core.errors)
        else:
            raise error


def parse_data(site):
    base = op.dirname(__file__)

    originals = []
    for fn in os.listdir(op.join(base, 'originals')):
        if fn.endswith('.yaml'):
            originals.extend(yaml.safe_load(open(op.join(base, 'originals', fn), encoding="utf-8")))
    def sort_key(game):
        name = game_name(game)
        # Always sort SCUMM first
        if name == 'SCUMM':
            return '0'
        if name.startswith('The '):
            return name[4:]
        return name
    originals = natsorted(originals, key=sort_key, alg=ns.IGNORECASE)
    print(str(len(originals)) + ' games in total')
    validate_with_schema(originals, 'schema/originals.yaml')

    clones = []
    for fn in sorted(os.listdir(op.join(base, 'games'))):
        if fn.endswith('.yaml'):
            clones.extend(yaml.safe_load(open(op.join(base, 'games', fn), encoding="utf-8")))
    print(str(len(clones)) + ' clones in total')
    validate_with_schema(clones, 'schema/games.yaml')

    errors = []
    originals_map = {}

    for item in originals:
        name = game_name(item)

        if name in originals_map:
            errors.append({
                "name": name,
                "error": "Duplicate original game '%s'" % name
            })

        originals_map[name] = item

    if len(errors) > 0:
        show_errors(errors)

    def has_invalid_status(clone) -> bool:
        # Tools and only tools must have N/A status
        return (clone["type"] == "tool") != (clone["status"] == "N/A")

    for clone in clones:
        if 'originals' not in clone:
            show_errors([{
                "name": clone["name"],
                "error": "Unable to find 'remakes' or 'clones' in game"
            }])

        for original in clone['originals']:
            if original not in originals_map:
                errors.append({
                    "name": clone["name"],
                    "error": "Original game '%s' not found" % original
                })

        if isinstance(clone['updated'], str):
            clone['updated'] = datetime.strptime(clone['updated'], "%Y-%m-%d").date()
        if isinstance(clone.get('added'), str):
            clone['added'] = datetime.strptime(clone['added'], "%Y-%m-%d").date()
        if clone.get('added', date.min) > clone['updated']:
            errors.append({
                "name": clone['name'],
                "error": "Added date is after updated date"
            })
        if has_invalid_status(clone):
            errors.append({
                "name": clone["name"],
                "error": "Has invalid status - tools must be N/A"
            })

    if len(errors) > 0:
        show_errors(errors)

    for item in originals:
        # Recombine originals and clones
        combined = copy.deepcopy(item)
        name = game_name(combined)

        combined['games'] = [
            clone for clone in clones
            if name in clone['originals']
        ]
        parse_items(site, combined, 'games')
    # Deduplicate clones by using a dictionary
    site.new_games = {
        clone['name']: (_names, meta, clone)
        for (_names, meta, clone) in sorted([
            (game.names, game.meta, clone)
            for game in site.games
            for clone in game.clones
            if clone['is_updated']
        ], key=lambda args: args[2]['updated'], reverse=True)
    }
