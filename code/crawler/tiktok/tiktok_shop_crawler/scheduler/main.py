import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.mysql import get_crawl_info
from .order_processing import scheduled_fetch_all_orders
from .token_processing import scheduled_refresh_token


async def add_tiktok_shop_refresh_job(
    scheduler: AsyncIOScheduler,
    refresh_token: str,
    job_id: str,
    vada_uid: str,
    account_name: str,
):
    try:
        # Schedule the token refresh job
        scheduler.add_job(
            scheduled_refresh_token,
            trigger=IntervalTrigger(minutes=60),  # Refresh every hour
            kwargs={"refresh_token": refresh_token},
            id=job_id,
            name=f"Refresh TikTokShop Token for Shop: {account_name} for Vada UID: {vada_uid}",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        logging.info(
            f"[Scheduler] Added TikTokShop Token refresh job for Shop: {account_name} for Vada UID: {vada_uid}"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding TikTokShop Token refresh job for Shop: {account_name} for Vada UID: {vada_uid}: {str(e)}",
            exc_info=True,
        )


async def add_tiktok_shop_crawl_job(
    scheduler: AsyncIOScheduler,
    access_token: str,
    index_name: str,
    job_id: str,
    vada_uid: str,
    account_name: str,
    crawl_interval: int,
):
    now = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    try:
        # Crawl immediately for the first time
        await scheduled_fetch_all_orders(
            access_token=access_token,
            start_date=ninety_days_ago,
            end_date=now,
            index_name=index_name,
            vada_uid=vada_uid,
            account_name=account_name,
        )

        # The first job will crawl T-1 -> T0 with 2h interval
        scheduler.add_job(
            scheduled_fetch_all_orders,
            trigger=IntervalTrigger(minutes=crawl_interval),
            kwargs={
                "access_token": access_token,
                "index_name": index_name,
                "vada_uid": vada_uid,
                "account_name": account_name,
            },
            id=job_id,
            name=f"Fetch TikTokShop Order for Shop: {account_name}, Index: {index_name} every {crawl_interval} minutes",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        # We may create another job for crawling ealier T with longer interval

        logging.info(
            f"[Scheduler] Added TikTokShop Order job for Shop: {account_name}, Index: {index_name} every {crawl_interval} minutes"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding TikTokShop Order job for Shop: {account_name}, Index: {index_name}: {str(e)}",
            exc_info=True,
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        # Fetch crawl info specific to TikTok Shop
        crawl_info = await get_crawl_info("tiktok_shop")
        current_jobs = {job.id: job for job in scheduler.get_jobs()}

        for info in crawl_info:
            crawl_id = info["crawl_id"]
            vada_uid = info["vada_uid"]
            account_name = info["account_name"]
            index_name = info["index_name"]
            access_token = info["access_token"]
            refresh_token = info["refresh_token"]
            crawl_interval = info["crawl_interval"]

            crawl_job_id = f"crawl_order_{crawl_id}"
            refresh_job_id = f"refresh_token_{crawl_id}"

            await add_tiktok_shop_refresh_job(
                scheduler=scheduler,
                refresh_token=refresh_token,
                job_id=refresh_job_id,
                vada_uid=vada_uid,
                account_name=account_name,
            )

            await add_tiktok_shop_crawl_job(
                scheduler=scheduler,
                access_token=access_token,
                index_name=index_name,
                job_id=crawl_job_id,
                vada_uid=vada_uid,
                account_name=account_name,
                crawl_interval=crawl_interval,
            )

            # Remove the old job from current_jobs
            if crawl_job_id in current_jobs:
                del current_jobs[crawl_job_id]
            if refresh_job_id in current_jobs:
                del current_jobs[refresh_job_id]

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
