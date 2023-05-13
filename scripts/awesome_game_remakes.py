"""
Scrape Awesome Game Remakes and find games OSGC doesn't have

To run, install from pip:
- aiohttp
- markdown
- lxml
"""
import aiohttp
import asyncio
import markdown
import re

from lxml import etree

from scripts.utils import games

URL = "https://raw.githubusercontent.com/radek-sprta/awesome-game-remakes/master/README.md"
BLACKLIST_PATTERNS = [
  re.compile(pat) for pat in [
    "https://awesome.re",
    "^#.+",
  ]
]

async def main():
  # Find links from AGR
  async with aiohttp.ClientSession() as session:
    async with session.get(URL) as resp:
        content = await resp.text()
  md = markdown.markdown(content)
  doc = etree.fromstring(f"<div>{md}</div>")
  urls = set()
  for link in doc.xpath("//a"):
    url = link.attrib["href"]
    for pat in BLACKLIST_PATTERNS:
      if pat.match(url):
        break
    else:
      urls.add(url)
  # Find URLs and repos from OSGC
  osgc_urls = set()
  for game in games():
    if repo := game.get("repo", ""):
      osgc_urls.add(repo)
    if url := game.get("repo", ""):
      osgc_urls.add(url)
  # Print URLS that OSGC doesn't have
  for url in urls - osgc_urls:
    print(url)

if __name__ == "__main__":
    asyncio.run(main())
