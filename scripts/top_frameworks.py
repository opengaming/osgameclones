import os
import re
from collections import Counter, defaultdict

from pathlib import Path

import yaml


def main():
    c = Counter()
    framework_langs = defaultdict(Counter)
    for p in Path('games').iterdir():
        if p.is_file() and p.suffix == ".yaml":
            games = yaml.safe_load(open(p, encoding="utf-8"))
            for game in games:
                for framework in game.get("framework", []):
                    c[framework] += 1
                    for lang in game.get("lang", []):
                        framework_langs[framework][lang] += 1
    most_common = c.most_common(10)
    for framework, count in most_common:
        print(f"{framework}: {count}")
        print(framework_langs[framework].most_common(5))


if __name__ == "__main__":
    main()
