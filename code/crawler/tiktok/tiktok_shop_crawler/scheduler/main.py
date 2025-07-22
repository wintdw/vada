import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.mysql import get_crawl_info
from .order_processing import scheduled_fetch_all_orders, crawl_new_client
from .token_processing import scheduled_refresh_token


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
            await crawl_new_client(
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
            logging.info(f"Processing crawl info: {info}")

            crawl_id = info["crawl_id"]
            account_name = info["account_name"]
            index_name = info["index_name"]
            access_token = info["access_token"]
            refresh_token = info["refresh_token"]
            access_token_expiry = info["access_token_expiry"]
            refresh_token_expiry = info["refresh_token_expiry"]
            crawl_interval = info["crawl_interval"]
            last_crawl_time = info["last_crawl_time"]
            first_crawl = True
            if last_crawl_time:
                first_crawl = False

            job_id = f"crawl_order_{crawl_id}"

            # --- Check and refresh token if needed ---
            await scheduled_refresh_token(
                crawl_id=crawl_id,
                refresh_token=refresh_token,
                access_token_expiry=access_token_expiry,
                refresh_token_expiry=refresh_token_expiry,
            )

            # New crawl job
            if job_id not in current_jobs:
                await add_tiktok_shop_crawl_job(
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
                logging.info(
                    f"[Scheduler] Removed TikTokShop job_id '{left_job_id}' as it is no longer valid"
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
