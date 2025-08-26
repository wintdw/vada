import logging
from datetime import datetime

from handler.crawl_info import get_crawl_info
from .crawl import crawl_daily_tiktokshop


async def schedule_daily_tiktokshop(crawl_id: str):
    """
    This will call crawl_daily_tiktokshop if the time condition is met
    """
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    account_name = crawl_info[0]["account_name"]

    next_crawl_time = datetime.fromisoformat(crawl_info[0]["next_crawl_time"])
    now = datetime.now()

    # If not yet time for next crawl, skip
    if now < next_crawl_time:
        logging.debug(
            f"[{account_name}] [Daily Crawl Scheduler] CrawlID {crawl_id}: skip (now={now}, next={next_crawl_time})"
        )
        return

    crawl_response = await crawl_daily_tiktokshop(crawl_id)
    logging.info(
        f"[{account_name}] [Daily Crawl Scheduler] Finish crawling with ID {crawl_id}"
    )
