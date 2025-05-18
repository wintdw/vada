import logging
import asyncio
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram  # type: ignore

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from handler.report import fetch_google_reports
from handler.mysql import get_google_ad_crawl_info


google_ad_crawl_total = Counter(
    "google_ad_crawl_total", "Total number of crawls", ["crawl_id"]
)
google_ad_crawl_sucess = Counter(
    "google_ad_crawl_sucess", "Total number of successful crawls", ["crawl_id"]
)
google_ad_crawl_latency = Histogram(
    "google_ad_crawl_latency_seconds",
    "Latency of Google Ad crawls in seconds",
    ["crawl_id"],
)


async def scheduled_fetch_google_reports(
    refresh_token: str,
    index_name: str,
    crawl_id: str,
    vada_uid: str = "",
    account_email: str = "",
):
    """
    Function to call the fetch_google_reports function for a specific Google Ad account.
    """
    logging.info(
        f"[Scheduler] Starting scheduled fetch of Google Ads reports for {index_name}"
    )
    try:
        google_ad_crawl_total.labels(crawl_id=crawl_id).inc()

        # Calculate dates
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        if vada_uid and account_email:
            mappings = {
                "vada_uid": vada_uid,
                "account_email": account_email,
            }
        else:
            mappings = None

        with google_ad_crawl_latency.labels(crawl_id=crawl_id).time():
            await asyncio.wait_for(
                fetch_google_reports(
                    refresh_token=refresh_token,
                    start_date=start_date,
                    end_date=end_date,
                    persist=True,
                    es_index=index_name,
                    mappings=mappings,
                ),
                timeout=600,
            )

        google_ad_crawl_sucess.labels(crawl_id=crawl_id).inc()
        logging.info(
            f"[Scheduler] Successfully fetched Google Ads reports for {index_name}"
        )
    except Exception as e:
        logging.error(
            f"[Scheduler] Error fetching Google Ads reports for {index_name}: {str(e)}",
            exc_info=True,
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def update_jobs():
        # Fetch Google Ad crawl info
        google_ad_info = await get_google_ad_crawl_info()
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
                    # Update the job if parameters have changed
                    scheduler.add_job(
                        scheduled_fetch_google_reports,
                        trigger=IntervalTrigger(minutes=crawl_interval),
                        kwargs={
                            "refresh_token": refresh_token,
                            "index_name": index_name,
                            "crawl_id": crawl_id,
                            "vada_uid": vada_uid,
                            "account_email": account_email,
                        },
                        id=job_id,
                        name=f"Fetch Google Ads Reports for ID: {crawl_id}, Index: {index_name} every {crawl_interval} minutes",
                        replace_existing=True,
                        misfire_grace_time=30,
                        max_instances=1,
                    )
                    logging.info(
                        f"Updated Google Ads Reports job for ID: {crawl_id}, Index: {index_name} every {crawl_interval} minutes"
                    )
                else:
                    logging.info(
                        f"Job for ID: {crawl_id}, Index: {index_name} is unchanged. Skipping update."
                    )
            else:
                # Add the job to the scheduler if it doesn't exist
                scheduler.add_job(
                    scheduled_fetch_google_reports,
                    trigger=IntervalTrigger(minutes=crawl_interval),
                    kwargs={
                        "refresh_token": refresh_token,
                        "index_name": index_name,
                        "crawl_id": crawl_id,
                    },
                    id=job_id,
                    name=f"Fetch Google Ads Reports for ID: {crawl_id}, Index: {index_name} every {crawl_interval} minutes",
                    misfire_grace_time=30,
                    max_instances=1,
                )
                logging.info(
                    f"Added Google Ads Reports job for ID: {crawl_id}, Index: {index_name} every {crawl_interval} minutes"
                )

            # Remove the job from current_jobs as it is still valid
            if job_id in current_jobs:
                del current_jobs[job_id]

        # Remove jobs that are no longer in the google_ad_info
        for job_id in current_jobs:
            # dont remove update_jobs
            if job_id != "update_jobs":
                # Remove the job from the scheduler
                scheduler.remove_job(job_id)
                logging.info(
                    f"Removed Google Ads Reports job with ID: {job_id} as it is no longer needed"
                )

    # Schedule the update_jobs function to run every 20 minutes
    scheduler.add_job(
        update_jobs,
        trigger=IntervalTrigger(minutes=20),
        id="update_jobs",
        name="Update Google Ads Reports jobs every 20 minutes",
        replace_existing=False,
        misfire_grace_time=30,
        max_instances=1,
    )

    # Run the update_jobs function once at startup
    await update_jobs()

    return scheduler
