import os.path as op
from datetime import datetime, timedelta

import yaml
from cyrax import events

def names(item):
    return item.get('names') or [item['name']]

def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))
    site.clones = []
    site.reimplementations = []
    for item in data:
        if 'added' in item:
            item['added'] = datetime.strptime(item['added'], '%Y-%m-%d').date()
            item['new'] = item['added'] < (datetime.now() - timedelta(days=30))

        if 'clones' in item:
            site.clones.append((names(item), item['clones']))
        if 'reimplementations' in item:
            site.reimplementations.append((names(item),
                                           item['reimplementations']))


def callback(site):
    events.events.connect('traverse-started', parse_data)
