from collections import Counter, defaultdict

from scripts.utils import games


def main():
    c = Counter()
    framework_langs = defaultdict(Counter)
    for game in games():
        for framework in game.get("frameworks", []):
            c[framework] += 1
            for lang in game.get("langs", []):
                framework_langs[framework][lang] += 1
    most_common = c.most_common(10)
    for framework, count in most_common:
        print(f"{framework}: {count}")
        print(framework_langs[framework].most_common(5))


if __name__ == "__main__":
    main()
