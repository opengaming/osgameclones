from pathlib import Path
from typing import Iterable

import yaml


def originals() -> Iterable[dict]:
    for p in Path("originals").iterdir():
        if p.is_file() and p.suffix == ".yaml":
            originals = yaml.safe_load(open(p, encoding="utf-8"))
            for original in originals:
                yield original


def games() -> Iterable[dict]:
    for p in Path('games').iterdir():
        if p.is_file() and p.suffix == ".yaml":
            games = yaml.safe_load(open(p, encoding="utf-8"))
            for game in games:
                yield game
