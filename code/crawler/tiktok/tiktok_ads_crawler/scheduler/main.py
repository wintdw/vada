import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.metrics import update_crawl_metrics
from repository.crawl_info import get_crawl_info
from .crawl import crawl_first_tiktokad, crawl_daily_tiktokad_scheduler


async def init_scheduler():
    async def update_jobs():
        try:
            await update_crawl_metrics()

            crawl_infos = await get_crawl_info()
            for info in crawl_infos:
                crawl_id = info["crawl_id"]
                last_crawl_time = info["last_crawl_time"]
                first_crawl = not bool(last_crawl_time)

                if first_crawl:
                    # fire and forget
                    asyncio.create_task(crawl_first_tiktokad(crawl_id=crawl_id))

                # run regular crawl regardless first_crawl
                await crawl_daily_tiktokad_scheduler(crawl_id=crawl_id)
        except Exception as e:
            logging.error(f"Exception in update jobs: {e}", exc_info=True)

    # Schedule the update_jobs function to run every 1m
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update TiktokAd jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
