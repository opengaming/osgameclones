"""
Scrape ScummVM supported games at good or excellent level, and create YAML clone templates

Uses libraries:
- beautifulsoup4
- httpx
- tenacity
"""
import re
from pathlib import Path
from typing import Container, Optional

import httpx
import yaml
from bs4 import BeautifulSoup
from tenacity import stop_after_attempt, retry, wait_exponential
from utils import originals

SCUMMVM_LIST = "https://www.scummvm.org/compatibility/"
SCUMMVM_BASE_URL = "https://www.scummvm.org"
SUPPORT_LEVELS = {"Good", "Excellent"}
PLATFORM_ALIASES = {
    "Apple IIgs": "Apple II",
    "Atari ST": "Atari",
    "Macintosh": "Classic Mac OS",
    "Steam": "Windows",
    "Tandy Color Computer 3": "CoCo",
}
# These games are not games or compilations/demos that shouldn't have their own game entries
BLACKLIST = {
    "Inside the Chest",
    "King's Questions",
    "Passport to Adventure (Indiana Jones and the Last Crusade, The Secret of Monkey Island, Loom)",
    "Mission Supernova 1",
    "Mission Supernova 2"
}


def main():
    # Get list of OSGC originals
    osgc_originals = set()
    for original in originals():
        osgc_originals.add(original["name"])
        for name in original.get("names", []):
            osgc_originals.add(name)

    # Get platforms
    platforms = yaml.safe_load(open(Path("schema") / "originals.yaml", encoding="utf-8"))["schema;platforms"]["enum"]

    # Get list of games
    resp = httpx.get(SCUMMVM_LIST)
    content = resp.text
    soup = BeautifulSoup(content, "html.parser")
    game_links = {}
    for td_name, td_support_level in zip(soup.find_all("td", class_="gameFullName"), soup.find_all("td", class_="gameSupportLevel")):
        # Filter out those that aren't good enough
        if td_support_level.text not in SUPPORT_LEVELS:
            continue
        name = td_name.text.strip()
        # Filter out engines
        if name.endswith(" games"):
            continue
        # Filter out blacklist
        if name in BLACKLIST:
            continue
        # Use name in parens if present
        if match := re.match(r".+ \((.+)\)", name):
            name = match.group(1)
        game_links[name] = SCUMMVM_BASE_URL + td_name.a.attrs["href"]

    # Generate originals list
    origs = list(game_links)

    # Filter out those we already have (match case-insensitive)
    def game_is_in_original(game: str) -> bool:
        if game in osgc_originals:
            return True
        # Try case-insensitive
        if game.lower() in {o.lower() for o in osgc_originals}:
            return True
        # Try using the name before or after the colon
        if (match := re.match(r"(.+):(.+)", game)) and (match.group(1).strip() in osgc_originals or match.group(2).strip() in osgc_originals):
           return True
        # Try matching without certain punctuation
        if game.replace("!", "") in {o.replace("!", "") for o in osgc_originals}:
            return True
        return False
    missing_originals = {original for original in origs if not game_is_in_original(original)}
    print("ScummVM originals:")
    for original in sorted(missing_originals):
        print(f"- {original}")

    for original in missing_originals:
        if game_info := scrape_game_info(game_links[original], platforms):
            print(yaml.dump(game_info))


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=2, max=10))
def scrape_game_info(link: str, platforms: Container[str]) -> Optional[dict]:
    # Go to game subpage
    resp = httpx.get(link)
    content = resp.text
    soup = BeautifulSoup(content, "html.parser")

    # Don't add games that aren't clones
    if soup.find("a", string="ScummVM Freeware Games"):
        return None

    # Generate game entry, with name
    game = {
        "name": soup.find("td", class_="gameFullName").text,
        "external": {},
        "platforms": [],
        "meta": {
            "genres": [],
            "themes": [],
        }
    }
    # Add Supported Platforms
    supported_platforms_title = soup.find("h3", string="Supported Platforms")
    if supported_platforms_lis := supported_platforms_title.find_next_sibling("ul"):
        for li in supported_platforms_lis.find_all("li"):
            platform = li.text.strip()
            platform = PLATFORM_ALIASES.get(platform, platform)
            if platform not in platforms:
                print(f"{platform=} unknown")
            elif platform not in game["platforms"]:
                game["platforms"].append(platform)

    # Find links
    if wikipedia_link := soup.find("a", string="Wikipedia"):
        game["external"]["wikipedia"] = wikipedia_name(wikipedia_link.attrs["href"])
    if mobygames_link := soup.find("a", string="MobyGames"):
        game["external"]["website"] = mobygames_link.attrs["href"]
    if not wikipedia_link and not mobygames_link:
        # Use ScummVM wiki as fallback
        if scummvm_link := soup.find("a", string="ScummVM Wiki"):
            game["external"]["website"] = scummvm_link.attrs["href"]
        else:
            print(f"Cannot find link for {game['name']}")

    return game


def wikipedia_name(link: str) -> str:
    """
    >>> wikipedia_name("https://en.wikipedia.org/wiki/Operation_Stealth")
    'Operation Stealth'
    """
    return link.split("/")[-1].replace("_", " ")


if __name__ == "__main__":
    main()
