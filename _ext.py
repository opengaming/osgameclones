import sys
import pprint
import os.path as op
from datetime import date, timedelta

import yaml
from cyrax import events


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
    return item.get('names') or [item['name']]


def mark_new(entry):
    added = entry.get('added') or date(1970, 1, 1)
    return dict(entry,
                new=(date.today() - added) < timedelta(days=30))


def parse_tags(site, games, tag):
    for game in games:
        if tag in game:
            if not getattr(site, tag, False):
                setattr(site, tag, {})

            if isinstance(game[tag], basestring):
                game[tag] = [game[tag]]

            for t in game[tag]:
                tagObj = getattr(site, tag, False)
                if not tagObj.get(t, False):
                    tagObj[t] = {'tag_count': 0}
                tagObj[t]['tag_count'] += 1


def parse_item(site, item, key):
    if key in item and validate(item, key):
        if not getattr(site, key, False):
            setattr(site, key, [])

        parse_tags(site, item[key], 'lang')
        getattr(site, key).append((names(item), map(mark_new, item[key])))


def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))

    for item in data:
        parse_item(site, item, 'clones')
        parse_item(site, item, 'reimplementations')


def callback(site):
    events.events.connect('traverse-started', parse_data)
