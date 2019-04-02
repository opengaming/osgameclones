import copy
import sys
import pprint
import os, os.path as op
from datetime import date, timedelta
from collections import OrderedDict
from functools import partial
import urlparse

import yaml
from cyrax import events
from natsort import natsorted, ns
from pykwalify.core import Core
from unidecode import unidecode


def abort(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def validate(item, key):
    for name in names(item):
        if not (isinstance(name, basestring) or
                (len(name) == 2 and
                 all(isinstance(x, basestring) for x in name))):
            abort('Error: %r should be a string or a list of two strings' % name)
    games = item[key]
    if (not isinstance(games, list) or
        not all(map(lambda x: isinstance(x, dict), games))):
        print 'Error: this should be a list of dicts:'
        abort(pprint.pformat(games))
    return names, games


def names(item):
    return [item['name']] + item.get('names', [])


def game_name(game):
    return game['name'][0] if isinstance(game['name'], list) else game['name']


def parse_tag(tag):
    return tag.replace(' ', '-').lower()


def parse_unicode(text):
    if type(text) == str:
        text = unicode(text)
    if type(text) == unicode:
        return unidecode(text)
    if type(text) in [list, tuple]:
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
            val_type = type(val)

            if val_type == str or val_type == unicode:
                tags.append(parse_tag(val))
                tags.append(parse_unicode_tag(val))
            elif val_type == list:
                tags += map(parse_tag, val)
                tags += map(parse_unicode_tag, val)
            else:
                abort('Error: %s\'s key "%s" is not valid (%s)' %
                    (entry['name'], key, val_type.__name__))

    result = []
    for tag in tags:
        if tag not in result:
            result.append(tag)

    return result


def parse_global_tags(site, item, tag):
    if tag in item:
        if not getattr(site, tag, False):
            setattr(site, tag, {})

        if isinstance(item[tag], basestring):
            item[tag] = [item[tag]]

        for t in item[tag]:
            tagObj = getattr(site, tag, False)
            if not tagObj.get(t, False):
                tagObj[t] = {'tag_count': 0}
            tagObj[t]['tag_count'] += 1

    setattr(site, tag, OrderedDict(sorted(getattr(site, tag, {}).items())))


def parse_item(entry, entry_tags=[], meta={}, meta_tags=[]):
    updated = entry.get('updated') or date(1970, 1, 1)
    result = dict(entry,
                  new=(date.today() - updated) < timedelta(days=30),
                  tags=parse_tags(entry, entry_tags) + parse_tags(meta, meta_tags))

    if "repo" in result:
        domain = urlparse.urlparse(result["repo"]).netloc
        ext = os.path.splitext(result["repo"])[1]

        if "github.com" in domain:
            result["repoiconname"] = "github"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "GitHub"
        elif (".google.com" in domain or
              "googlecode.com" in domain):
            result["repoiconname"] = "google"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "Google Code"
        elif "bitbucket.org" in domain:
            result["repoiconname"] = "bitbucket"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "Bitbucket"
        elif "gitlab.com" in domain:
            result["repoiconname"] = "gitlab"
            result["repoiconstyle"] = "fab"
            result["repotitle"] = "GitLab"
        elif ext in (".zip", ".tar", ".tgz", ".tbz2", ".bz2", ".xz", ".rar"):
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

    parse_fn = partial(parse_item, entry_tags=game_tags, meta=meta, meta_tags=meta_tags)

    for game in item[key]:
        parse_global_tags(site, game, 'lang')

    item = (names(item), meta, map(parse_fn, item[key]))
    getattr(site, key).append(item)


def show_error(game_name, error_str):
    print('\033[91m' + '  ' + game_name.encode('utf-8') + '\033[0m')
    print('    ' + error_str)


def show_errors(errors):
    print('\n')
    for error in errors:
        show_error(error["name"], error["error"])
    print('\n  ' + str(len(errors)) + ' errors\n')
    sys.exit(1)


def show_validation_errors(data, validation_errors):
    errors = []
    for error in validation_errors:
        path = error.path.split('/')
        game = data[int(path[1])]
        name = game_name(game)

        errors.append({"name": name, "error": error.__repr__()})

    show_errors(errors)


def parse_data(site):
    base = op.dirname(__file__)

    originals = []
    for fn in os.listdir(op.join(base, 'originals')):
        if fn.endswith('.yaml'):
            originals.extend(yaml.load(open(op.join(base, 'originals', fn))))
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

    try:
        core = Core(source_data=originals, schema_files=['schema/originals.yaml'])
        core.validate(raise_exception=True)
    except Exception as error:
        if len(core.errors) > 0:
            show_validation_errors(originals, core.errors)
        else:
            raise error

    clones = []
    for fn in sorted(os.listdir(op.join(base, 'games'))):
        if fn.endswith('.yaml'):
            clones.extend(yaml.load(open(op.join(base, 'games', fn))))
    print(str(len(clones)) + ' clones in total')

    try:
        core = Core(source_data=clones, schema_files=['schema/games.yaml'])
        core.validate(raise_exception=True)
    except Exception as error:
        if len(core.errors) > 0:
            show_validation_errors(clones, core.errors)
        else:
            raise error

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
        parse_global_tags(site, item.get('meta', {}), 'genre')
        # Recombine originals and clones
        combined = copy.deepcopy(item)
        name = game_name(combined)

        combined['games'] = [
            clone for clone in clones
            if name in clone['originals']
        ]
        parse_items(site, combined, 'games')


def callback(site):
    events.events.connect('traverse-started', parse_data)
