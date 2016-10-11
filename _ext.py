import sys
import pprint
import os.path as op
from datetime import date, timedelta
from collections import OrderedDict
from functools import partial

import yaml
from cyrax import events
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


def parse_tag(tag):
    return tag.replace(' ', '-').lower()


def parse_tags(entry, fields):
    tags = []

    for field in fields:
        if field in entry:
            if isinstance(entry[field], basestring):
                tags.append(parse_tag(entry[field]))
            else:
                tags += map(parse_tag, entry[field])

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
    return dict(entry,
                new=(date.today() - updated) < timedelta(days=30),
                tags=parse_tags(entry, entry_tags) + parse_tags(meta, meta_tags))


def parse_items(site, item, key):
    if key in item and validate(item, key):
        if not getattr(site, key, False):
            setattr(site, key, [])

        meta = item.get('meta', {})
        meta_tags = ['genre', 'subgenre', 'theme']
        game_tags = ['status', 'development', 'license', 'lang', 'framework']
        parse_fn = partial(parse_item, entry_tags=game_tags, meta=meta, meta_tags=meta_tags)

        for game in item[key]:
            parse_global_tags(site, game, 'lang')
        getattr(site, key).append((names(item), meta, map(parse_fn, item[key])))


def show_validation_errors(data, errors):
    print('\n')
    for error in errors:
        path = error.path.split('/')
        game = data[int(path[1])]
        name = game.get('name')
        print('\033[91m' + '  ' + str(name) + '\033[0m')
        print('    ' + error.__repr__())
    print('\n  ' + str(len(errors)) + ' errors\n')
    sys.exit(1)


def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))

    try:
        core = Core(source_data=data, schema_files=['schema.yaml'])
        core.validate(raise_exception=True)
    except Exception as error:
        if len(core.errors) > 0:
            show_validation_errors(data, core.errors)
        else:
            raise error

    for item in data:
        parse_global_tags(site, item.get('meta', {}), 'genre')
        parse_items(site, item, 'remakes')
        parse_items(site, item, 'clones')


def callback(site):
    events.events.connect('traverse-started', parse_data)
