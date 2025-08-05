import logging
from datetime import datetime, timedelta
from typing import Dict

from handler.nhanh import crawl_nhanh_data
from handler.persist import post_processing, enrich_doc
from handler.crawl_info import update_crawl_time, get_crawl_info


async def crawl_first_nhanh(crawl_id: str):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    chunk = timedelta(days=2)
    current_end = end_date

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    index_name = crawl_info[0]["index_name"]
    business_id = crawl_info[0]["business_id"]
    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    logging.info(
        f"[{business_id}] [First Crawl] Crawling from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    )

    while current_end > start_date:
        current_start = max(current_end - chunk, start_date)

        crawl_response = await crawl_nhanh_data(
            business_id=business_id,
            access_token=access_token,
            from_date=current_start.strftime("%Y-%m-%d"),
            to_date=current_end.strftime("%Y-%m-%d"),
        )
        logging.info(
            f"[{business_id}] [First Crawl Chunk] Result from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}: {crawl_response.get('status')}"
        )

        # Send to the datastore
        await post_processing(
            [enrich_doc(order) for order in crawl_response.get("orders", [])],
            index_name,
        )

        current_end = current_start  # move backward

    await update_crawl_time(crawl_id, crawl_interval)


async def crawl_daily_nhanh(
    crawl_id: str, start_date: str = "", end_date: str = ""
) -> Dict:
    """
    start_date and end_date are for manual crawl only
    """
    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return {}

    index_name = crawl_info[0]["index_name"]
    business_id = crawl_info[0]["business_id"]
    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    logging.info(
        f"[{business_id}] [Daily Crawl] Crawling from {start_date} to {end_date}"
    )

    crawl_response = await crawl_nhanh_data(
        business_id=business_id,
        access_token=access_token,
        from_date=start_date,
        to_date=end_date,
    )

    # Send to the datastore
    await post_processing(
        [enrich_doc(order) for order in crawl_response.get("orders", [])],
        index_name,
    )
    await update_crawl_time(crawl_id, crawl_interval)
    crawl_response.pop("orders", None)

    logging.info(
        f"[{business_id}] [Daily Crawl] Result from {start_date} to {end_date}: {crawl_response}"
    )

    return crawl_response


async def crawl_daily_nhanh_scheduler(crawl_id: str):
    """
    This will call crawl_daily_nhanh if the time condition is met
    """
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    business_id = crawl_info[0]["business_id"]

    next_crawl_time = datetime.fromisoformat(crawl_info[0]["next_crawl_time"])
    now = datetime.now()

    # If not yet time for next crawl, skip
    if now < next_crawl_time:
        logging.debug(
            f"[{business_id}] [Daily Crawl Scheduler] CrawlID {crawl_id}: skip (now={now}, next={next_crawl_time})"
        )
        return

    crawl_response = await crawl_daily_nhanh(crawl_id)
    logging.info(
        f"[{business_id}] [Daily Crawl Scheduler] Finish crawl ID {crawl_id}: {crawl_response}"
    )
