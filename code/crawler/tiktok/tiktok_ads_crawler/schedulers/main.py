import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from tools.logger import get_logger
from .crawl import crawl_first_tiktok_ad, crawl_daily_tiktok_ad
from repositories.crawl_info import get_crawl_info

logger = get_logger(__name__)


async def add_tiktok_ad_crawl_job(
    scheduler: AsyncIOScheduler,
    job_id: str,
    crawl_id: str,
    access_token: str,
    index_name: str,
    crawl_interval: int,
    account_name: str = "",  # For logging purpose
    first_crawl: bool = True,  # Whether to start the crawl immediately
):
    try:
        if first_crawl:
            logger.info(
                f"[First Crawl] Processing job for: {account_name} with crawl_id: {crawl_id}"
            )
            # Split 1-year crawl into 12 jobs of 1 month each
            await crawl_first_tiktok_ad(
                crawl_id=crawl_id,
                access_token=access_token,
                index_name=index_name,
                crawl_interval=crawl_interval,
            )

        # The regular job will crawl T-1 -> T0 with 2h interval
        scheduler.add_job(
            crawl_daily_tiktok_ad,
            trigger=IntervalTrigger(minutes=crawl_interval),
            kwargs={
                "crawl_id": crawl_id,
                "access_token": access_token,
                "index_name": index_name,
                "crawl_interval": crawl_interval,
            },
            id=job_id,
            name=f"Fetch TikTokAd for {account_name} every {crawl_interval} minutes",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        # We may create another job for crawling ealier T with longer interval

        logger.info(
            f"[Scheduler] Added TikTokAd job for: {account_name} every {crawl_interval} minutes"
        )
    except Exception as e:
        logger.error(
            f"[Scheduler] Error adding TikTokAd job for: {account_name}: {str(e)}",
            exc_info=True,
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        # Fetch crawl info specific to TikTok Shop
        crawl_infos = await get_crawl_info()
        current_jobs = {job.id: job for job in scheduler.get_jobs()}

        for info in crawl_infos:
            logger.info(f"Processing crawl: {info}")

            crawl_id = info["crawl_id"]
            account_name = info["account_name"]
            index_name = info["index_name"]
            access_token = info["access_token"]
            crawl_interval = info["crawl_interval"]
            last_crawl_time = info["last_crawl_time"]
            first_crawl = True
            if last_crawl_time:
                first_crawl = False

            job_id = f"crawl_tta_{crawl_id}"

            # New crawl job
            if job_id not in current_jobs:
                await add_tiktok_ad_crawl_job(
                    scheduler=scheduler,
                    job_id=job_id,
                    crawl_id=crawl_id,
                    access_token=access_token,
                    index_name=index_name,
                    crawl_interval=crawl_interval,
                    account_name=account_name,
                    first_crawl=first_crawl,
                )
            else:
                del current_jobs[job_id]

        # Remove jobs that are no longer in the crawl_info
        for left_job_id in current_jobs:
            if left_job_id != "update_jobs":
                scheduler.remove_job(left_job_id)
                logger.info(
                    f"[Scheduler] Removed TikTokAd job_id '{left_job_id}' as it is no longer valid"
                )

    # Schedule the update_jobs function to run every 1m
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update TikTokAd jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
