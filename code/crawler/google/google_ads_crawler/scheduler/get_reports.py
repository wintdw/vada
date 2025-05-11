import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from router.report import fetch_google_reports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scheduled_fetch_google_reports():
    """
    Function to call the fetch_google_reports function every a period of time.
    """
    try:
        # Call the fetch_google_reports function directly
        await fetch_google_reports(
            "your_refresh_token",
            start_date="2025-05-01",
            end_date="2025-05-31",
            persist=True,
            es_index="a_quang_nguyen_google_ad_report",
        )
        logger.info("[Scheduler] Successfully fetched Google Ads reports")
    except Exception as e:
        logger.error(
            f"[Scheduler] Error fetching Google Ads reports: {str(e)}", exc_info=True
        )


def init_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_fetch_google_reports,
        trigger=IntervalTrigger(minutes=5),
        id="fetch_google_reports_job",
        name="Fetch Google Ads Reports every 2 hours",
        replace_existing=True,
    )
    return scheduler
