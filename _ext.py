import os.path as op
from datetime import date, timedelta

import yaml
from cyrax import events

def names(item):
    return item.get('names') or [item['name']]

def mark_new(item):
    if 'added' in item:
        item['new'] = (date.today() - item['added']) < timedelta(days=30)
    return item

def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))
    site.clones = []
    site.reimplementations = []
    for item in data:

        if 'clones' in item:
            site.clones.append(
                (names(item), map(mark_new, item['clones'])))
        if 'reimplementations' in item:
            site.reimplementations.append(
                (names(item), map(mark_new, item['reimplementations'])))


def callback(site):
    events.events.connect('traverse-started', parse_data)
