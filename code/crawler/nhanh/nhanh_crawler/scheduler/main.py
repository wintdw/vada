import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.crawl_info import get_crawl_info
from .crawl import crawl_first_nhanh, crawl_daily_nhanh_scheduler


async def schedule_nhanh_crawl_job(
    crawl_id: str,
    first_crawl: bool = False,  # Whether to start the crawl immediately
):
    tasks = []
    if first_crawl:
        tasks.append(asyncio.create_task(crawl_first_nhanh(crawl_id=crawl_id)))

    tasks.append(asyncio.create_task(crawl_daily_nhanh_scheduler(crawl_id=crawl_id)))

    await asyncio.gather(*tasks)


async def init_scheduler():
    running_tasks = {}

    async def update_jobs():
        crawl_infos = await get_crawl_info()

        for info in crawl_infos:
            crawl_id = info["crawl_id"]
            last_crawl_time = info["last_crawl_time"]
            first_crawl = not bool(last_crawl_time)

            existing = running_tasks.get(crawl_id)
            if existing and not existing.done():
                logging.info(f"[{crawl_id}] skipping - task still running")
                continue

            task = asyncio.create_task(
                schedule_nhanh_crawl_job(crawl_id=crawl_id, first_crawl=first_crawl)
            )
            running_tasks[crawl_id] = task

    # Schedule the update_jobs function to run every 1m
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update Nhanh jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
