import re

import httpx
from mistletoe import Document
from mistletoe.block_token import Heading, List
from scripts.utils import games, originals

INSPIRATION_PATTERN = re.compile(r"(.+) \[\d+\]")
INSPIRED_PATTERN = re.compile(r"Inspired entries: (.+)")
# OSGL name to OSGC alias
ALIASES = {
    "Alone in the Dark series": "Alone in the Dark",
    "Anno (series)": "Anno series",
    "BioWare's Aurora engine": "Neverwinter Nights",
    "Blake Stone: Aliens of Gold": "Blake Stone: Planet Strike",
    "Blasteroids": "Asteroids",
    "Caesar 3": "Caesar III",
    "Civilization series": "Civilization",
    "Company of Heroes: Opposing Fronts": "Company of Heroes",
    "Company of Heroes: Tales of Valor": "Company of Heroes",
}
# Games that aren't interesting enough or weren't closed source
BLACKLIST = {
    "arithmetic",
    "Black Shades",
    "Blob Wars Attrition",
    "Blobby Volley",
    "Chromium B.S.U.",
    "CorsixTH",
    "Crossfire",
    "Cube",
    "Cube 2: Sauerbraten",
    "CUBE engine",
    "Daimonin",
    "TuxMath",
}


def main():
    resp = httpx.get("https://raw.githubusercontent.com/Trilarion/opensourcegames/master/inspirations.md")
    doc = Document(resp.text)
    # Only look at level 2 headings
    children = [child for child in doc.children if not isinstance(child, Heading) or child.level == 2]
    inspiration = None
    osgl_games = {}
    for child in children:
        if isinstance(child, Heading):
            inspiration = INSPIRATION_PATTERN.match(child.children[0].content).group(1)
        else:
            assert isinstance(child, List)
            for subchild in child.children:
                text = subchild.children[0].children[0].content
                if matches := INSPIRED_PATTERN.match(text):
                    inspireds = matches.group(1).split(", ")
                    osgl_games[inspiration] = inspireds
    # Find games and clones from OSGC
    osgc_originals = set()
    for original in originals():
        osgc_originals.add(original["name"])
        for name in original.get("names", []):
            osgc_originals.add(name)
    for game in osgl_games:
        if game in BLACKLIST:
            continue
        alias = ALIASES.get(game)
        if game not in osgc_originals and (not alias or alias not in osgc_originals):
            print(f"Missing original: {game}")
    osgc_games = set(game["name"] for game in games())
    for game, inspireds in osgl_games.items():
        for inspired in inspireds:
            if inspired not in osgc_games:
                print(f"Missing clone: {inspired} (inspired by {game})")


if __name__ == "__main__":
    main()
