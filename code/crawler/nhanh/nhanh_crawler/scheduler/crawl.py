import logging
from datetime import datetime, timedelta
from typing import Dict

from handler.nhanh import crawl_nhanh_data
from handler.persist import post_processing, enrich_doc
from handler.crawl_info import update_crawl_time, get_crawl_info


async def crawl_first_nhanh(crawl_id: str):
    # Crawl 1 year of data, split into 30-day chunks (from latest to oldest)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
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

    while current_end > start_date:
        current_start = max(current_end - chunk, start_date)

        crawl_response = await crawl_nhanh_data(
            business_id=business_id,
            access_token=access_token,
            from_date=current_start.strftime("%Y-%m-%d"),
            to_date=current_end.strftime("%Y-%m-%d"),
        )
        logging.info(
            f"[First Crawl] CrawlID {crawl_id} from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}: {crawl_response}"
        )

        # Check if the crawl response is successful
        if crawl_response.get("status") != "success":
            logging.error(f"[First Crawl] Error: {crawl_response}", exc_info=True)
            return

        # Send to the datastore
        await post_processing(
            [enrich_doc(order) for order in crawl_response.get("orders", [])],
            index_name,
        )

        current_end = current_start  # move backward

    await update_crawl_time(crawl_id, crawl_interval)


async def crawl_daily_nhanh(crawl_id: str):
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    index_name = crawl_info[0]["index_name"]
    business_id = crawl_info[0]["business_id"]
    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    crawl_response = await crawl_nhanh_data(
        business_id=business_id,
        access_token=access_token,
        from_date=start_date,
        to_date=end_date,
    )

    # Check if the crawl response is successful
    if crawl_response.get("status") != "success":
        logging.error(f"[First Crawl] Error: {crawl_response}", exc_info=True)
        return

    # Send to the datastore
    await post_processing(
        [enrich_doc(order) for order in crawl_response.get("orders", [])],
        index_name,
    )
    await update_crawl_time(crawl_id, crawl_interval)

    logging.info(
        f"[Daily Crawl] CrawlID {crawl_id} from {start_date} to {end_date}: {crawl_response}"
    )
