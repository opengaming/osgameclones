#!/usr/bin/env python3

import html
import json
import os, os.path as op
import shutil
import functools
import argparse
import logging
from distutils.dir_util import copy_tree
from pathlib import Path

import unidecode

import jinja2
from pykwalify_webform.renderer import Renderer
from slugify import slugify
from yaml import safe_load

import _ext

HERE = Path(__file__).parent


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
    updated = max(game['updated'] for names, meta, game in site.new_games.values())
    render_to('feed.xml', f'{target}/feed.xml', site=site, updated=updated)
    for game in site.games:
        render_to(
            'game.html',
            f'{target}/{game.slug}/index.html',
            site=site,
            game=game,
            title=f"{game.names[0]} clones - OSGC",
            description=f"List of open source clones and remakes for {game.names[0]}"
        )
        render_data(f"{target}/{game.slug}/data.json", game.item)
    # Render data for edit game/clone forms
    clones = {clone["name"]: clone for game in site.games for clone in game.clones}
    for name, clone in clones.items():
        render_data(f"{target}/_clones/{slugify(name)}.json", clone)


def normalize(text):
    if not text:
        return ''
    return html.escape(unidecode.unidecode(text.lower()))


def render_game_form(schema: str, out_path: str, form_name: str, value=None):
    log.info(f"Rendering game form {schema=} -> {out_path}")
    with open(schema) as f:
        schemata = safe_load(f)
    renderer = Renderer(schemata, HERE / "templates/forms")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(renderer.render("", name=form_name, value=value, static_url="/_add_form"))


def render_data(out_path: str, value):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(value, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(description='Render OSGC')
    parser.add_argument('-d', '--dest', default='_build')
    args = parser.parse_args()

    env().filters['normalize'] = normalize
    env().filters['slugify'] = slugify
    render_all(args.dest)

    # Render add game forms
    render_game_form("schema/games.yaml", f"{args.dest}/add_game.html", "Add Game")
    render_game_form("schema/originals.yaml", f"{args.dest}/add_original.html", "Add Original")

    # Copy static files
    copy_tree(str(HERE / "templates/forms/static"), f"{args.dest}/_add_form")


if __name__ == '__main__':
    main()
