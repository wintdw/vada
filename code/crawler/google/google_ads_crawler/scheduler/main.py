import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.crawl_metrics import update_crawl_metrics
from handler.mysql import get_crawl_info
from .crawl import crawl_new_client, crawl_daily


async def schedule_google_ad_crawl_job(
    crawl_id: str,
    first_crawl: bool = False,
):
    tasks = []
    if first_crawl:
        tasks.append(asyncio.create_task(crawl_new_client(crawl_id=crawl_id)))

    tasks.append(asyncio.create_task(crawl_daily(crawl_id=crawl_id)))
    await asyncio.gather(*tasks)


async def init_scheduler():
    running_tasks = {}

    async def update_jobs():
        await update_crawl_metrics()

        google_ad_info = await get_crawl_info()

        for info in google_ad_info:
            crawl_id = info["crawl_id"]
            last_crawl_time = info["last_crawl_time"]
            first_crawl = not bool(last_crawl_time)

            # Avoid duplicate tasks
            existing = running_tasks.get(crawl_id)
            if existing and not existing.done():
                logging.info(f"[{crawl_id}] skipping - task still running")
                continue

            task = asyncio.create_task(
                schedule_google_ad_crawl_job(crawl_id=crawl_id, first_crawl=first_crawl)
            )
            running_tasks[crawl_id] = task

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update Google Ads Reports jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    await update_jobs()
    return scheduler
