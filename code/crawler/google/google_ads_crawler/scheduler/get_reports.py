import logging
import asyncio
from datetime import datetime, timedelta
from prometheus_client import Counter  # type: ignore

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from router.report import fetch_google_reports
from handler.mysql import get_google_ad_crawl_info


google_ad_crawl_total = Counter(
    "google_ad_crawl_total", "Total number of crawls", ["crawl_id"]
)
google_ad_crawl_failure = Counter(
    "google_ad_crawl_failure", "Total number of failed crawls", ["crawl_id"]
)


async def scheduled_fetch_google_reports(
    refresh_token: str, index_name: str, crawl_id: str
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

        # Set a timeout for the fetch_google_reports function
        await asyncio.wait_for(
            fetch_google_reports(
                refresh_token=refresh_token,
                start_date=start_date,
                end_date=end_date,
                persist=True,
                es_index=index_name,
            ),
            timeout=300,  # Timeout in seconds (e.g., 5 minutes)
        )
        logging.info(
            f"[Scheduler] Successfully fetched Google Ads reports for {index_name}"
        )
    except Exception as e:
        google_ad_crawl_failure.labels(crawl_id=crawl_id).inc()

        logging.error(
            f"[Scheduler] Error fetching Google Ads reports for {index_name}: {str(e)}",
            exc_info=True,
        )


async def init_scheduler():
    scheduler = AsyncIOScheduler()

    # Fetch Google Ad crawl info
    google_ad_info = await get_google_ad_crawl_info()

    for info in google_ad_info:
        crawl_id = info["crawl_id"]
        index_name = info["index_name"]
        refresh_token = info["refresh_token"]
        crawl_interval = info["crawl_interval"]

        scheduler.add_job(
            scheduled_fetch_google_reports,
            trigger=IntervalTrigger(minutes=crawl_interval),
            args=[refresh_token, index_name, crawl_id],
            id=f"fetch_google_reports_job_{crawl_id}",
            name=f"Fetch Google Ads Reports for ID: {crawl_id}, Index: {index_name} every {crawl_interval} minutes",
            replace_existing=True,
        )
        logging.info(
            f"Added Google Ads Reports job for ID: {crawl_id}, Index: {index_name} every {crawl_interval} minutes"
        )

    return scheduler
