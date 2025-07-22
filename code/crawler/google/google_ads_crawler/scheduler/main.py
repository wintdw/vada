import logging
import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.report import fetch_google_reports
from handler.mysql import get_crawl_info
from .crawl import crawl_new_client


async def add_google_ad_crawl_job(
    scheduler: AsyncIOScheduler,
    job_id: str,
    crawl_id: str,
    refresh_token: str,
    index_name: str,
    vada_uid: str,
    account_name: str,
    crawl_interval: int,
    first_crawl: bool = False,  # Whether to start the crawl immediately
):
    try:
        if first_crawl:
            # Crawl immediately for the first time
            await crawl_new_client(
                crawl_id=crawl_id,
                refresh_token=refresh_token,
                index_name=index_name,
                vada_uid=vada_uid,
                account_name=account_name,
                crawl_interval=crawl_interval,
            )

        # The first job will crawl T-1 -> T0 with 2h interval
        scheduler.add_job(
            fetch_google_reports,
            trigger=IntervalTrigger(minutes=crawl_interval),
            kwargs={
                "refresh_token": refresh_token,
                "persist": True,
                "index_name": index_name,
                "vada_uid": vada_uid,
                "account_name": account_name,
                "start_date": (datetime.now() - timedelta(days=1))
                .date()
                .strftime("%Y-%m-%d"),
                "end_date": datetime.now().date().strftime("%Y-%m-%d"),
            },
            id=job_id,
            name=f"Fetch Google Ads Reports for Account: {account_name}, Index: {index_name} every {crawl_interval} minutes",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        # We may create another job for crawling ealier T with longer interval

        logging.info(
            f"[Scheduler] Added Google Ads Reports job for Account: {account_name}, Index: {index_name} every {crawl_interval} minutes"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding Google Ads Reports job for Account: {account_name}, Index: {index_name}: {str(e)}"
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        # Fetch Google Ad crawl info
        google_ad_info = await get_crawl_info()
        tasks = []
        current_jobs = {job.id: job for job in scheduler.get_jobs()}

        for info in google_ad_info:
            crawl_id = info["crawl_id"]
            vada_uid = info["vada_uid"]
            account_name = info["account_name"]
            index_name = info["index_name"]
            refresh_token = info["refresh_token"]
            crawl_interval = info["crawl_interval"]
            last_crawl_time = info["last_crawl_time"]
            first_crawl = True
            if last_crawl_time:
                first_crawl = False

            job_id = f"fetch_gga_reports_job_{crawl_id}"

            tasks.append(
                asyncio.create_task(
                    add_google_ad_crawl_job(
                        scheduler=scheduler,
                        job_id=job_id,
                        crawl_id=crawl_id,
                        refresh_token=refresh_token,
                        index_name=index_name,
                        vada_uid=vada_uid,
                        account_name=account_name,
                        crawl_interval=crawl_interval,
                        first_crawl=first_crawl,
                    )
                )
            )

            # Remove the old job from current_jobs
            if job_id in current_jobs:
                del current_jobs[job_id]

        # Remove jobs that are no longer in the google_ad_info
        for job_id in current_jobs:
            # dont remove update_jobs
            if job_id != "update_jobs":
                scheduler.remove_job(job_id)
                logging.info(
                    f"[Scheduler] Removed Google Ads Reports job with ID: {job_id} as it is no longer valid"
                )

        # Wait for all add_google_ad_crawl_job tasks to finish
        if tasks:
            await asyncio.gather(*tasks)

    # Schedule the update_jobs function to run every 1m
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=1),
        id="update_jobs",
        name="Update Google Ads Reports jobs every 1 minute",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
