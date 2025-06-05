import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.mysql import get_crawl_info
from .processing import fetch_all_orders


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
        await fetch_all_orders(
            access_token=access_token,
            start_date=ninety_days_ago,
            end_date=now,
            index_name=index_name,
            vada_uid=vada_uid,
            account_name=account_name,
        )

        # The first job will crawl T-1 -> T0 with 2h interval
        scheduler.add_job(
            fetch_all_orders,
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

            job_id = f"fetch_tiktokshop_order_job_{crawl_id}"
            existing_job = scheduler.get_job(job_id)

            # Check if the job already exists
            if existing_job:
                # Check if any parameters have changed
                existing_trigger = existing_job.trigger
                existing_kwargs = existing_job.kwargs

                if (
                    # allow changes of interval, access_token, index_name
                    existing_kwargs["index_name"] != index_name
                    or existing_kwargs["access_token"] != access_token
                    or existing_trigger.interval.total_seconds() != crawl_interval * 60
                ):
                    # Update the job with new parameters
                    await add_tiktok_shop_crawl_job(
                        scheduler=scheduler,
                        access_token=access_token,
                        index_name=index_name,
                        job_id=job_id,
                        vada_uid=vada_uid,
                        account_name=account_name,
                        crawl_interval=crawl_interval,
                    )
                # job unchanged
                else:
                    logging.info(
                        f"[Scheduler] TikTokShop Order Job for Account: {account_name}, Index: {index_name} is unchanged. Skipping update."
                    )
            else:
                # Add a new job
                await add_tiktok_shop_crawl_job(
                    scheduler=scheduler,
                    access_token=access_token,
                    index_name=index_name,
                    job_id=job_id,
                    vada_uid=vada_uid,
                    account_name=account_name,
                    crawl_interval=crawl_interval,
                )

            # Remove the old job from current_jobs
            if job_id in current_jobs:
                del current_jobs[job_id]

        # Remove jobs that are no longer in the crawl_info
        for job_id in current_jobs:
            # dont remove update_jobs
            if job_id != "update_jobs":
                scheduler.remove_job(job_id)
                logging.info(
                    f"[Scheduler] Removed TikTokShop Order job with ID: {job_id} as it is no longer valid"
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
