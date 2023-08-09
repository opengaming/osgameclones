"""
Scrape ScummVM supported games at good or excellent level, and create YAML clone templates

Uses libraries:
- aiohttp
- beautifulsoup4
- tenacity
"""
import asyncio
from pathlib import Path
from typing import Container, Optional

import aiohttp
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

async def main():
    # Get list of OSGC originals
    osgc_originals = set()
    for original in originals():
        osgc_originals.add(original["name"])
        for name in original.get("names", []):
            osgc_originals.add(name)

    # Get platforms
    platforms = yaml.safe_load(open(Path("schema") / "originals.yaml", encoding="utf-8"))["schema;platforms"]["enum"]

    # Get list of games
    async with aiohttp.ClientSession() as session:
        async with session.get(SCUMMVM_LIST) as resp:
            content = await resp.text()
        soup = BeautifulSoup(content, "html.parser")
        game_links = {}
        for td_name, td_support_level in zip(soup.find_all("td", class_="gameFullName"), soup.find_all("td", class_="gameSupportLevel")):
            # Filter out those that aren't good enough
            if td_support_level.text not in SUPPORT_LEVELS:
                continue
            # Filter out engines
            if td_name.text.endswith(" games"):
                continue
            game_links[td_name.text] = SCUMMVM_BASE_URL + td_name.a.attrs["href"]

        # Generate originals list
        origs = list(game_links)

        # Filter out those we already have
        missing_originals = {original for original in origs if original not in osgc_originals}
        print("ScummVM originals:")
        for original in sorted(missing_originals):
            print(f"- {original}")

        for original in missing_originals:
            if game_info := await scrape_game_info(session, game_links[original], platforms):
                print(yaml.dump(game_info))


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=2, max=10))
async def scrape_game_info(session: aiohttp.ClientSession, link: str, platforms: Container[str]) -> Optional[dict]:
    # Go to game subpage
    async with session.get(link) as resp:
        content = await resp.text()
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
    asyncio.run(main())
