import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.report import fetch_google_reports
from handler.mysql import get_crawl_info


async def add_google_ad_crawl_job(
    scheduler: AsyncIOScheduler,
    refresh_token: str,
    index_name: str,
    job_id: str,
    vada_uid: str,
    account_email: str,
    crawl_interval: int,
):
    now = datetime.now().strftime("%Y-%m-%d")
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        # Crawl immediately for the first time
        await fetch_google_reports(
            refresh_token=refresh_token,
            start_date=thirty_days_ago,
            end_date=now,
            persist=True,
            index_name=index_name,
            vada_uid=vada_uid,
            account_email=account_email,
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
                "account_email": account_email,
            },
            id=job_id,
            name=f"Fetch Google Ads Reports for Email: {account_email}, Index: {index_name} every {crawl_interval} minutes",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
        )
        # We may create another job for crawling ealier T with longer interval

        logging.info(
            f"[Scheduler] Added Google Ads Reports job for Email: {account_email}, Index: {index_name} every {crawl_interval} minutes"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error adding Google Ads Reports job for Email: {account_email}, Index: {index_name}: {str(e)}"
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        # Fetch Google Ad crawl info
        google_ad_info = await get_crawl_info("google_ad")
        current_jobs = {job.id: job for job in scheduler.get_jobs()}

        for info in google_ad_info:
            crawl_id = info["crawl_id"]
            vada_uid = info["vada_uid"]
            account_email = info["account_email"]
            index_name = info["index_name"]
            refresh_token = info["refresh_token"]
            crawl_interval = info["crawl_interval"]

            job_id = f"fetch_google_reports_job_{crawl_id}"
            existing_job = scheduler.get_job(job_id)

            # Check if the job already exists
            if existing_job:
                # Check if any parameters have changed
                existing_trigger = existing_job.trigger
                existing_kwargs = existing_job.kwargs

                if (
                    existing_kwargs["index_name"] != index_name
                    or existing_kwargs["refresh_token"] != refresh_token
                    or existing_trigger.interval.total_seconds() != crawl_interval * 60
                ):
                    # Update the job with new parameters
                    await add_google_ad_crawl_job(
                        scheduler=scheduler,
                        refresh_token=refresh_token,
                        index_name=index_name,
                        job_id=job_id,
                        vada_uid=vada_uid,
                        account_email=account_email,
                        crawl_interval=crawl_interval,
                    )
                # job unchanged
                else:
                    logging.info(
                        f"[Scheduler] Job for Email: {account_email}, Index: {index_name} is unchanged. Skipping update."
                    )
            else:
                # Add a new job
                await add_google_ad_crawl_job(
                    scheduler=scheduler,
                    refresh_token=refresh_token,
                    index_name=index_name,
                    job_id=job_id,
                    vada_uid=vada_uid,
                    account_email=account_email,
                    crawl_interval=crawl_interval,
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
