"""
Check game URLs and repos for broken links
"""
import asyncio
import httpx
from bs4 import BeautifulSoup

from scripts.utils import games


async def check_link(client: httpx.AsyncClient, q: asyncio.Queue):
    while True:
        try:
            game, url, more_checks = await q.get()
        except asyncio.CancelledError:
            break
        print(f"Checking {game['name']} / {url}...")
        try:
            resp = await client.get(url, timeout=30.0, follow_redirects=True)
            if not resp.is_success:
                print(f"{url} returned {resp.status_code} ({game['name']})")
            elif more_checks:
                check_domain_content(url, resp.text)
        except httpx.RequestError as exc:
            print(f"{url} failed with error: {exc} ({game['name']})")
        finally:
            q.task_done()


async def main():
    q = asyncio.Queue()
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits) as client:
        # start workers
        worker_tasks = []
        for i in range(10):
            task = asyncio.create_task(check_link(client, q))
            worker_tasks.append(task)
        # add urls to queue
        for game in games():
            print(f"Checking {game['name']}...")
            if "repo" in game:
                await q.put((game, game["repo"], False))
            if "url" in game:
                await q.put((game, game["url"], True))
            for img in game.get("images", []):
                await q.put((game, img, False))
            # TODO: check videos
        # wait for tasks to complete
        print("Waiting for workers...")
        await q.join()
        # stop workers
        for task in worker_tasks:
            task.cancel()
        await asyncio.gather(*worker_tasks, return_exceptions=True)


def check_domain_content(url, text):
    # Red flags in content
    casino_keywords = ['casino', 'betting', 'poker', 'blackjack', 'roulette', 'gambling']
    scam_keywords = ['viagra', 'crypto giveaway', 'click here to claim', 'you won', 'urgent action required']
    parked_keywords = ['domain for sale', 'buy this domain', 'sedo', 'afternic', 'parkingcrew', 'bodis']

    # Content keyword matching
    if any(k in text for k in casino_keywords):
        print(f"{url} contains casino keywords")
    if any(k in text for k in scam_keywords):
        print(f"{url} contains scam keywords")
    if any(k in text for k in parked_keywords):
        print(f"{url} contains parked keywords")

    # Check title/meta for generic parking
    soup = BeautifulSoup(text, 'html.parser')
    title = soup.title.get_text().lower() if soup.title else ''
    if any(k in title for k in ['domain', 'for sale', 'buy', 'parked']):
        print(f"{url} has suspicious title")


if __name__ == "__main__":
    asyncio.run(main())
