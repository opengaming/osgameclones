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


def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))

    site.clones = [
        (names(item), map(mark_new, item['clones']))
        for item in data
        if 'clones' in item and validate(item, 'clones')]
    site.reimplementations = [
        (names(item), map(mark_new, item['reimplementations']))
        for item in data
        if 'reimplementations' in item and validate(item, 'reimplementations')]

    langs = []
    for item in data:
        if 'clones' in item: 
            which = item['clones']
        else: 
            which = item['reimplementations']
        for clone in which:
            if 'lang' in clone:
                lang = clone['lang']
                if isinstance(lang, basestring):
					lang = [lang]
                for l in lang:
                    langs.append(l)
    site.langs = list(set(langs))

def callback(site):
    events.events.connect('traverse-started', parse_data)
