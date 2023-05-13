"""
Check game URLs and repos for broken links

To run, install from pip:
- aiohttp
"""
import aiohttp
import asyncio

from scripts.utils import games


async def check_link(q):
    async with aiohttp.ClientSession() as session:
        while True:
            game, url = await q.get()
            async with session.get(url) as resp:
                if not resp.ok:
                    print(f"{url} returned {resp.status} ({game['name']})")
            q.task_done()


async def main():
    q = asyncio.Queue()
    # start workers
    worker_tasks = []
    for i in range(10):
        task = asyncio.create_task(check_link(q))
        worker_tasks.append(task)
    # add urls to queue
    for game in games():
        print(f"Checking {game['name']}...")
        if "repo" in game:
            await q.put((game, game["repo"]))
        if "url" in game:
            await q.put((game, game["url"]))
        for img in game.get("images", []):
            await q.put((game, img))
        # TODO: check videos
    # wait for tasks to complete
    print("Waiting for workers...")
    await q.join()
    # stop workers
    for task in worker_tasks:
        task.cancel()
    await asyncio.gather(*worker_tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
