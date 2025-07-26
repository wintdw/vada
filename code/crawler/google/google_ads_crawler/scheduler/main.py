import logging
import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.mysql import get_crawl_info
from .crawl import crawl_new_client, crawl_daily


async def add_google_ad_crawl_job(
    scheduler: AsyncIOScheduler,
    job_id: str,
    crawl_id: str,
    refresh_token: str,
    index_name: str,
    vada_uid: str,
    account_name: str,
    crawl_interval: int,
    first_crawl: bool = False,
):
    try:
        if first_crawl:
            await crawl_new_client(
                crawl_id=crawl_id,
                refresh_token=refresh_token,
                index_name=index_name,
                vada_uid=vada_uid,
                account_name=account_name,
                crawl_interval=crawl_interval,
            )

        scheduler.add_job(
            crawl_daily,
            trigger=IntervalTrigger(minutes=crawl_interval),
            kwargs={
                "crawl_id": crawl_id,
                "refresh_token": refresh_token,
                "index_name": index_name,
                "vada_uid": vada_uid,
                "account_name": account_name,
                "crawl_interval": crawl_interval,
            },
            id=job_id,
            name=f"Fetch Google Ads Reports for Account: {account_name}, Index: {index_name} every {crawl_interval} minutes",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )

    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding Google Ads Reports job for Account: {account_name}, Index: {index_name}: {str(e)}"
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        try:
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
                first_crawl = not last_crawl_time

                job_id = f"fetch_gga_reports_job_{crawl_id}"

                job = scheduler.get_job(job_id)
                should_update = False
                # job exists
                if job:
                    job_refresh_token = job.kwargs.get("refresh_token")
                    job_crawl_interval = (
                        job.trigger.interval.total_seconds() // 60
                        if hasattr(job.trigger, "interval")
                        else None
                    )
                    # Only update if refresh_token or crawl_interval changed
                    if (
                        job_refresh_token != refresh_token
                        or job_crawl_interval != crawl_interval
                    ):
                        should_update = True
                # new job
                else:
                    should_update = True

                if should_update:
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
                else:
                    logging.info(f"[Scheduler] Job {job_id} not updating")

                # Remove the old job from current_jobs if it was processed
                if job_id in current_jobs:
                    del current_jobs[job_id]

            # Remove jobs that are no longer in the google_ad_info
            for job_id in current_jobs:
                # dont remove update_jobs
                if job_id != "update_jobs":
                    scheduler.remove_job(job_id)
                    logging.info(
                        f"[Scheduler] Removed Job ID: {job_id} as it is no longer valid"
                    )

            # Wait for all add_google_ad_crawl_job tasks to finish
            if tasks:
                await asyncio.gather(*tasks)

        except Exception as e:
            logging.error(
                f"[Scheduler] Error updating Google Ads Reports jobs: {str(e)}",
                exc_info=True,
            )

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
