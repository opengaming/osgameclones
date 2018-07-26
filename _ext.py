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


def parse_tags(entry, keys):
    tags = []

    for key in keys:
        if key in entry:
            val = entry.get(key)
            val_type = type(val)

            if val_type == str or val_type == unicode:
                tags.append(parse_tag(val))
            elif val_type == list:
                tags += map(parse_tag, val)
            else:
                abort('Error: %s\'s key "%s" is not valid (%s)' %
                    (entry['name'], key, val_type.__name__))

    return tags


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
            result["repotitle"] = "Gitlab"
        elif ext in (".zip", ".tar", ".tgz", ".tbz2", ".bz2", ".xz", ".rar"):
            result["repoiconname"] = "box"
            result["repoiconstyle"] = "fas"
            result["repotitle"] = "Archive"

    return result


def parse_items(site, item, key):
    if key in item and validate(item, key):
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
            'multiplayer'
        ]

        meta = item.get('meta', {})
        parse_fn = partial(parse_item, entry_tags=game_tags, meta=meta, meta_tags=meta_tags)

        for game in item[key]:
            parse_global_tags(site, game, 'lang')
        getattr(site, key).append((names(item), meta, map(parse_fn, item[key])))


def show_validation_errors(data, errors):
    print('\n')
    for error in errors:
        path = error.path.split('/')
        game = data[int(path[1])]
        name = game_name(game)

        print('\033[91m' + '  ' + name.encode('utf-8') + '\033[0m')
        print('    ' + error.__repr__())
    print('\n  ' + str(len(errors)) + ' errors\n')
    sys.exit(1)


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

    for item in originals:
        parse_global_tags(site, item.get('meta', {}), 'genre')
        # Recombine originals and clones
        combined = copy.deepcopy(item)
        name = game_name(combined)
        combined_remakes = [
            clone for clone in clones
            if 'remakes' in clone and name in clone['remakes']
        ]
        if len(combined_remakes) > 0:
            combined['remakes'] = combined_remakes
        combined_clones = [
            clone for clone in clones
            if 'clones' in clone and name in clone['clones']
        ]
        if len(combined_clones) > 0:
            combined['clones'] = combined_clones
        parse_items(site, combined, 'remakes')
        parse_items(site, combined, 'clones')


def callback(site):
    events.events.connect('traverse-started', parse_data)
