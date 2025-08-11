import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.metrics import update_crawl_metrics
from handler.crawl_info import get_crawl_info
from .order import crawl_first_tiktokshop, crawl_daily_tiktokshop_scheduler
from .token import refresh_token_scheduler


async def schedule_tiktokshop_crawl_job(
    crawl_id: str,
    first_crawl: bool = False,  # Whether to start the crawl immediately
):
    tasks = []
    if first_crawl:
        tasks.append(asyncio.create_task(crawl_first_tiktokshop(crawl_id=crawl_id)))

    tasks.append(
        asyncio.create_task(crawl_daily_tiktokshop_scheduler(crawl_id=crawl_id))
    )

    await asyncio.gather(*tasks)


async def init_scheduler():
    running_tasks = {}

    async def update_jobs():
        try:
            await update_crawl_metrics()

            crawl_infos = await get_crawl_info()

            for info in crawl_infos:
                crawl_id = info["crawl_id"]
                last_crawl_time = info["last_crawl_time"]
                first_crawl = not bool(last_crawl_time)

                existing = running_tasks.get(crawl_id)
                if existing and not existing.done():
                    logging.debug(f"[{crawl_id}] skipping - task still running")
                    continue

                await refresh_token_scheduler(crawl_id=crawl_id)
                task = asyncio.create_task(
                    schedule_tiktokshop_crawl_job(
                        crawl_id=crawl_id, first_crawl=first_crawl
                    )
                )
                running_tasks[crawl_id] = task
        except Exception as e:
            logging.error(f"Exception in update jobs: {e}", exc_info=True)

    # Schedule the update_jobs function to run every 1m
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update TiktokShop jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
