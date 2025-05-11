import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from router.report import fetch_google_reports


async def scheduled_fetch_google_reports():
    """
    Function to call the fetch_google_reports function every a period of time.
    """
    logging.info("[Scheduler] Starting scheduled fetch of Google Ads reports")
    try:
        # Calculate dates
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Call the fetch_google_reports function directly
        await fetch_google_reports(
            request={
                "refresh_token": "your_refresh_token_here",  # Replace with actual refresh token
            },
            start_date=start_date,
            end_date=end_date,
            persist=True,
            es_index="a_quang_nguyen_google_ad_report",
        )
        logging.info("[Scheduler] Successfully fetched Google Ads reports")
    except Exception as e:
        logging.error(
            f"[Scheduler] Error fetching Google Ads reports: {str(e)}", exc_info=True
        )


def init_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_fetch_google_reports,
        trigger=IntervalTrigger(minutes=5),
        id="fetch_google_reports_job",
        name="Fetch Google Ads Reports every 5 minutes",
        replace_existing=True,
    )
    return scheduler
