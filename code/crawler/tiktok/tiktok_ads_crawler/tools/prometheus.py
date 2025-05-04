from prometheus_client import Gauge

from .logger import get_logger

logger = get_logger(__name__, 20)

active_crawl_jobs_gauge = Gauge("active_crawl_jobs", "Number of active jobs")

async def update_metrics():
    from repositories import select_crawl_history_by_crawl_status

    try:
        crawl_history = await select_crawl_history_by_crawl_status("in_progress")
        active_crawl_jobs_gauge.set(len(crawl_history))
        logger.info(f"Metrics updated")
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")