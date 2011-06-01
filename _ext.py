import os.path as op

import yaml
from cyrax import events


def parse_data(site):
    data = yaml.load(file(op.join(op.dirname(__file__), 'games.yaml')))
    site.clones = []
    site.reimplementations = []
    for item in data:
        if 'clones' in item:
            site.clones.append((item.get('names') or [item['name']],
                                item['clones']))
        if 'reimplementations' in item:
            site.reimplementations.append((item.get('names') or [item['name']],
                                           item['reimplementations']))


def callback(site):
    events.events.connect('traverse-started', parse_data)
