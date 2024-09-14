from pathlib import Path
from typing import Iterable

import yaml

PROJECT_ROOT_PATH = Path(__file__).parent.parent.resolve()


def originals() -> Iterable[dict]:
    for p in (PROJECT_ROOT_PATH / "originals").iterdir():
        if p.is_file() and p.suffix == ".yaml":
            originals = yaml.safe_load(open(p, encoding="utf-8"))
            for original in originals:
                yield original


def games() -> Iterable[dict]:
    for p in (PROJECT_ROOT_PATH / "games").iterdir():
        if p.is_file() and p.suffix == ".yaml":
            games = yaml.safe_load(open(p, encoding="utf-8"))
            for game in games:
                yield game
