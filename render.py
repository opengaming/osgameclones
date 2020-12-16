#!/usr/bin/env python3

import html
import os, os.path as op
import shutil
import functools
import argparse
import logging
import re
import unidecode

import jinja2
import _ext


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


DIR = op.dirname(__file__)


class Site:
    pass


@functools.lru_cache(10)
def env():
    return jinja2.Environment(loader=jinja2.FileSystemLoader(DIR))


@functools.lru_cache(10)
def ctx():
    site = Site()
    _ext.parse_data(site)
    return site


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def render_to(src, dst, **ctx):
    t = env().get_template(src)

    log.info(f'Rendering {src} -> {dst}')
    res = t.render(**ctx)

    os.makedirs(op.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(res)


def copy_to(src, dst):
    log.info(f'Copying {src} -> {dst}')
    shutil.copytree(src, dst)


def render_all(target):
    if op.exists(target):
        shutil.rmtree(target)

    copy_to('static', target + '/static')

    site = ctx()
    render_to('index.html', f'{target}/index.html', site=site)
    for game in ctx().games:
        name = slug(game[0][0])
        render_to('game.html', f'{target}/{name}/index.html', site=site, game=game)

        
def normalize(text):
    if not text:
        return ''
    return html.escape(unidecode.unidecode(text.lower()))


def main():
    parser = argparse.ArgumentParser(description='Render OSGC')
    parser.add_argument('-d', '--dest', default='_build')
    args = parser.parse_args()

    env().filters['normalize'] = normalize
    render_all(args.dest)


if __name__ == '__main__':
    main()
