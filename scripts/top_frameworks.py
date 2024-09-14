from collections import Counter, defaultdict

from scripts.utils import games

import pandas as pd


def main():
    c = Counter()
    framework_langs = defaultdict(Counter)
    for game in games():
        for framework in game.get("frameworks", []):
            c[framework] += 1
            for lang in game.get("langs", []):
                framework_langs[framework][lang] += 1
    most_common = c.most_common(10)
    rows = []
    for framework, count in most_common:
        framework_lang_counts = framework_langs[framework].most_common(5)
        row = {"framework": framework, "total": count}
        for i, lang in enumerate(framework_lang_counts):
            row[f"lang{i+1}"] = lang
        rows.append(row)
    df = pd.DataFrame(rows)
    print(df)


if __name__ == "__main__":
    main()
