import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.mysql import get_crawl_info
from .order_processing import scheduled_fetch_all_orders
from .token_processing import scheduled_refresh_token


async def add_tiktok_shop_refresh_job(
    scheduler: AsyncIOScheduler, job_id: str, crawl_id: str, refresh_token: str
):
    try:
        # Schedule the token refresh job
        scheduler.add_job(
            scheduled_refresh_token,
            trigger=IntervalTrigger(minutes=4320),  # Refresh every 3d
            kwargs={
                "crawl_id": crawl_id,
                "refresh_token": refresh_token,
            },
            id=job_id,
            name=f"Refresh TikTokShop Token for crawl_id {crawl_id}",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        logging.info(
            f"[Scheduler] Added TikTokShop Token refresh job for Crawl ID {crawl_id}"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding TikTokShop Token refresh job for Crawl ID {crawl_id}: {str(e)}",
            exc_info=True,
        )


async def add_tiktok_shop_first_crawl_jobs(
    crawl_id: str,
    access_token: str,
    index_name: str,
    crawl_interval: int,
):
    """Split the first 1-year crawl into jobs, each handling 7 days."""
    now = datetime.now()
    days_in_year = 365
    window = 7
    num_jobs = days_in_year // window + (1 if days_in_year % window else 0)
    for i in range(num_jobs):
        start_date = (now - timedelta(days=days_in_year - i * window)).strftime(
            "%Y-%m-%d"
        )
        # For the last job, end_date is tomorrow; otherwise, it's the end of the window
        if i < num_jobs - 1:
            end_date = (now - timedelta(days=days_in_year - (i + 1) * window)).strftime(
                "%Y-%m-%d"
            )
        else:
            end_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        await scheduled_fetch_all_orders(
            crawl_id=crawl_id,
            access_token=access_token,
            index_name=index_name,
            crawl_interval=crawl_interval,
            start_date=start_date,
            end_date=end_date,
        )


async def add_tiktok_shop_crawl_job(
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
            # Split 1-year crawl into 12 jobs of 1 month each
            await add_tiktok_shop_first_crawl_jobs(
                crawl_id=crawl_id,
                access_token=access_token,
                index_name=index_name,
                crawl_interval=crawl_interval,
            )

        # The regular job will crawl T-1 -> T0 with 2h interval
        scheduler.add_job(
            scheduled_fetch_all_orders,
            trigger=IntervalTrigger(minutes=crawl_interval),
            kwargs={
                "crawl_id": crawl_id,
                "access_token": access_token,
                "index_name": index_name,
                "crawl_interval": crawl_interval,
            },
            id=job_id,
            name=f"Fetch TikTokShop Order for Shop: {account_name} every {crawl_interval} minutes",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        # We may create another job for crawling ealier T with longer interval

        logging.info(
            f"[Scheduler] Added TikTokShop Order job for Shop: {account_name} every {crawl_interval} minutes"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding TikTokShop Order job for Shop: {account_name}: {str(e)}",
            exc_info=True,
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        # Fetch crawl info specific to TikTok Shop
        crawl_info = await get_crawl_info()
        current_jobs = {job.id: job for job in scheduler.get_jobs()}

        for info in crawl_info:
            # For debugging
            logging.info(f"Processing crawl info: {info}")

            crawl_id = info["crawl_id"]
            account_name = info["account_name"]
            index_name = info["index_name"]
            access_token = info["access_token"]
            refresh_token = info["refresh_token"]
            crawl_interval = info["crawl_interval"]
            last_crawl_time = info["last_crawl_time"]
            first_crawl = True
            if last_crawl_time:
                first_crawl = False

            crawl_job_id = f"crawl_order_{crawl_id}"
            refresh_job_id = f"refresh_token_{crawl_id}"

            # New refresh job
            if refresh_job_id not in current_jobs:
                await add_tiktok_shop_refresh_job(
                    scheduler=scheduler,
                    job_id=refresh_job_id,
                    crawl_id=crawl_id,
                    refresh_token=refresh_token,
                )
            else:
                del current_jobs[refresh_job_id]

            # New crawl job
            # Determine first crawl
            if crawl_job_id not in current_jobs:
                await add_tiktok_shop_crawl_job(
                    scheduler=scheduler,
                    job_id=crawl_job_id,
                    crawl_id=crawl_id,
                    access_token=access_token,
                    index_name=index_name,
                    crawl_interval=crawl_interval,
                    account_name=account_name,
                    first_crawl=first_crawl,
                )
            else:
                del current_jobs[crawl_job_id]

        # Remove jobs that are no longer in the crawl_info
        for left_job_id in current_jobs:
            # dont remove update_jobs
            if left_job_id != "update_jobs":
                scheduler.remove_job(left_job_id)
                logging.info(
                    f"[Scheduler] Removed TikTokShop Order job with ID: {left_job_id} as it is no longer valid"
                )

    # Schedule the update_jobs function to run every 1m
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update TikTokShop Order jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
