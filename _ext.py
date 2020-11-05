import copy
import sys
import pprint
import os, os.path as op
from datetime import date, datetime, timedelta
from collections import OrderedDict
from functools import partial
from urllib.parse import urlparse

import yaml
from natsort import natsorted, ns
from pykwalify.core import Core


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
    updated = entry.get('updated') or date(1970, 1, 1)
    if isinstance(updated, str):
        updated = datetime.strptime(updated, "%Y-%m-%d").date()
    result = dict(entry,
                  new=(date.today() - updated) < timedelta(days=30),
                  tags=parse_tags(entry, entry_tags) + parse_tags(meta, meta_tags),
                  updated=updated)

    if "repo" in result:
        # Try to add extra repo information, like icons, badges
        repo_parsed = urlparse(result["repo"])
        domain = repo_parsed.netloc
        ext = os.path.splitext(result["repo"])[1]

        if "github.com" in domain:
            try:
                # https://github.com/<user>/<repo>
                _, user, repo, *_ = repo_parsed.path.split("/")
            except ValueError:
                result["repoiconname"] = "github"
                result["repoiconstyle"] = "fab"
                result["repotitle"] = "GitHub"
            else:
                result["repobadge"] = f'<img class="badge lazyload" alt="GitHub stars" data-src="https://img.shields.io/github/stars/{user}/{repo}?style=flat-square&logo=github" src="https://img.shields.io/badge/stars-%3F-blue?style=flat-square&logo=github">'
        elif (".google.com" in domain or
              "googlecode.com" in domain):
            result["repoiconname"] = "google"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "Google Code"
        elif "bitbucket.org" in domain:
            result["repoiconname"] = "bitbucket"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "Bitbucket"
        elif "gitlab.com" in domain or domain.startswith("gitlab."):
            result["repoiconname"] = "gitlab"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "GitLab"
        elif "sourceforge.net" in domain:
            try:
                # https://sourceforge.net/projects/<repo>
                _, _, repo, *_ = repo_parsed.path.split("/")
            except ValueError:
                pass
            else:
                result["repobadge"] = f'<img class="badge lazyload" alt="Sourceforge downloads" data-src="https://img.shields.io/sourceforge/dt/{repo}?style=flat-square" src="http://img.shields.io/badge/downloads-%3F-brightgreen?style=flat-square">'
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

    meta_tags = ['genre', 'subgenre', 'theme']
    game_tags = [
        'status',
        'development',
        'lang',
        'framework',
        'content',
        'license',
        'multiplayer',
        'type'
    ]

    meta = item.get('meta', {})
    meta["names_ascii"] = parse_unicode(names(item))
    meta["external"] = item.get('external', {})
    parse_global_tags(site, meta, 'genre', item['name'])
    parse_global_tags(site, meta, 'subgenre', item['name'])
    parse_global_tags(site, meta, 'theme', item['name'])

    parse_fn = partial(parse_item, entry_tags=game_tags, meta=meta, meta_tags=meta_tags)

    for game in item[key]:
        parse_global_tags(site, game, 'lang', game['name'])

    item = (names(item), meta, [parse_fn(i) for i in item[key]])
    getattr(site, key).append(item)


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
