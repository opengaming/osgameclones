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
    "Anno 1404": "Anno series",
    "BioWare's Aurora engine": "Neverwinter Nights",
    "Blake Stone: Aliens of Gold": "Blake Stone: Planet Strike",
    "Blasteroids": "Asteroids",
    "Caesar 3": "Caesar III",
    "Civilization series": "Civilization",
    "Company of Heroes: Opposing Fronts": "Company of Heroes",
    "Company of Heroes: Tales of Valor": "Company of Heroes",
    "CrossFire 1981": "Crossfire",
    "CrossUO": "CrossUO: Ultima Online",
    "Final Fantasy series": "Final Fantasy",
    "Krush Kill 'n' Destroy": "Krush, Kill 'n' Destroy",
    "Marathon 2: Durandal": "Marathon 2",
    "Microprose Falcon 4.0 Combat Simulator": "Falcon",
    "Panzer General 2": "Panzer General",
    "Quake II": "Quake 2",
    "Quake III Arena": "Quake 3",
    "QUakeWorld": "Quake",
    "Runescape Classic": "RuneScape Classic",
    "S.T.A.L.K.E.R: Call of Pripyat": "S.T.A.L.K.E.R.: Call of Pripyat",
    "Settlers": "The Settlers",
    "Shobon Action": "Syobon Action",
    "Simon Says": "Simon",
    "Sonic the Hedgehog series": "Sonic the Hedgehog",
    "Super Methane Brothers for Wii and GameCube": "Super Methane Brothers (homebrew edition)",
    "Super Pang": "Pang",
    "The Incredible Machine series": "The Incredible Machine",
    "Ultima series": "Ultima",
    "Ultima Underworld 1": "Ultima Underworld",
    "Warcraft": "Warcraft: Orcs & Humans",
    "World of Might and Magic": "OpenEnroth",
    "Worms": "Worms Series",
    "X-COM: Enemy Unknown": "X-COM: UFO Defense",
}
# Games that aren't games, aren't interesting enough or weren't closed source
BLACKLIST = {
    "Angband",
    "arithmetic",
    "Black Shades",
    "Blob Wars Attrition",
    "Blobby Volley",
    "Brogue",
    "Cards Against Humanity",
    "Catan",
    "Chromium B.S.U.",
    "CorsixTH",
    "Cube",
    "Cube 2: Sauerbraten",
    "CUBE engine",
    "Daimonin",
    "Dragon Wars",
    "DragonBall",
    "Dungeon Crawl Stone Soup",
    "Elite Command",
    "Emerald Mine",     # clone of Boulder Dash
    "Eternal Lands",
    "Falcon's Eye",
    "Final Fantasy series",   # not specific enough
    "Flixel",
    "FooBillard",
    "GalaxyMage",
    "Game of Life",  # ambiguous, combines >1 game
    "GearHead",
    "GL-117",
    "Kobold's Quest",
    "Konquest",
    "LBreakout",
    "Linley's Dungeon Crawl",
    "Liquid War",
    "LÖVE",
    "Metroidvania",
    "Noiz2",
    "NScripter",
    "OGRE",
    "Open Dune",
    "RARS",
    "Red Eclipse",
    "Revenge Of The Cats: Ethernet",
    "sfxr",
    "Teeworlds",
    "The Clans",
    "The Mana World",
    "Tower defense",
    "Transball",
    "TuxMath",
    "Tux Racer",
    "Urho3D",
    "Vavoom",
    "Volleyball",
    "Webhangman",
    "XKobo",
    "XRay engine",
    "Xtank",
}
# Valid clones but we don't want to add it to OSGC unless we really have to
BLACKLIST_CLONES = {
    "Colonization too",  # halted long ago, status unknown
    "CommonDrops",  # halted, unknown status
    "DOOM-iOS",  # Superseded by DOOM-iOS2
    "Slot-Racers",  # 404, inactive
    "Story of a Lost Sky",  # halted, unclear how good/playable it is
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
    osgc_games = {game["name"] for game in games()}
    osgl_inspireds = {
        inspired
        for inspireds in osgl_games.values()
        for inspired in inspireds
    }
    for game in osgl_games:
        if game in BLACKLIST:
            continue
        # Exclude games that are open source clones to begin with
        if game in osgc_games and game not in osgc_originals:
            continue
        # Exclude transitive inspirations - we only want the originals
        if game in osgl_inspireds:
            continue
        alias = ALIASES.get(game)
        if game not in osgc_originals and (not alias or alias not in osgc_originals):
            print(f"Missing original: {game}")
    for inspired in osgl_inspireds:
        if inspired in BLACKLIST_CLONES:
            continue
        if inspired not in osgc_games:
            print(f"Missing clone: {inspired}")


if __name__ == "__main__":
    main()
