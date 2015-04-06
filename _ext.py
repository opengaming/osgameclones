import sys
import os.path as op
from datetime import date, timedelta

import yaml
from cyrax import events


def abort(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def validate(names, games):
    for name in names:
        if not (isinstance(name, basestring) or
                (len(name) == 2 and
                 all(isinstance(x, basestring) for x in name))):
            abort('%r should be a string or a list of two strings' % name)
    return names, games


def names(item):
    return item.get('names') or [item['name']]


def mark_new(item):
    added = item.get('added') or date(1970, 1, 1)
    return dict(item,
                new=(date.today() - added) < timedelta(days=30))


def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))

    site.clones = [
        validate(names(item), map(mark_new, item['clones']))
        for item in data
        if 'clones' in item]
    site.reimplementations = [
        validate(names(item), map(mark_new, item['reimplementations']))
        for item in data
        if 'reimplementations' in item]


def callback(site):
    events.events.connect('traverse-started', parse_data)
