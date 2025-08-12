import logging
from datetime import datetime, timedelta
from typing import Dict

from handler.persist import post_processing
from handler.report import fetch_google_reports
from handler.mysql import update_crawl_time, get_crawl_info


async def crawl_new_client(crawl_id: str):
    """
    Initial crawl for a new client, crawling 1 year of data in monthly chunks.
    """

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    refresh_token = crawl_info[0]["refresh_token"]
    index_name = crawl_info[0]["index_name"]
    account_name = crawl_info[0]["account_name"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    now = datetime.now()
    start_date = now - timedelta(days=365)
    chunk = timedelta(days=30)
    current_start = start_date

    logging.info(
        f"[{account_name}] [First Crawl] Starting initial crawl from {current_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
    )
    while current_start < now:
        current_end = min(current_start + chunk, now)
        report_response = await fetch_google_reports(
            refresh_token=refresh_token,
            start_date=current_start.strftime("%Y-%m-%d"),
            end_date=current_end.strftime("%Y-%m-%d"),
        )
        logging.info(
            f"[{account_name}] [First Crawl Chunk] Chunk Crawl from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}: {report_response.get('report', {}).get('total_reports', 0)} reports"
        )
        await post_processing(
            report_response.get("report", {}).get("reports", []),
            index_name,
        )
        current_start = current_end

    await update_crawl_time(crawl_id, crawl_interval)


async def crawl_daily(crawl_id: str, start_date: str = "", end_date: str = "") -> Dict:
    """
    start_date and end_date are for manual crawl only
    """
    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return {}

    refresh_token = crawl_info[0]["refresh_token"]
    index_name = crawl_info[0]["index_name"]
    account_name = crawl_info[0]["account_name"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    logging.info(
        f"[{account_name}] [Daily Crawl] Crawling from {start_date} to {end_date}"
    )

    crawl_response = await fetch_google_reports(
        refresh_token=refresh_token, start_date=start_date, end_date=end_date
    )
    await post_processing(
        crawl_response.get("report", {}).get("reports", []),
        index_name,
    )
    await update_crawl_time(crawl_id, crawl_interval)

    return {
        "status": "success",
        "date_start": start_date,
        "date_end": end_date,
        "total_reports": crawl_response["report"]["total_reports"],
    }


async def schedule_daily_crawl(crawl_id: str):
    """
    This will call crawl_daily if the time condition is met
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

    crawl_response = await crawl_daily(crawl_id)
    logging.info(
        f"[{account_name}] [Daily Crawl Scheduler] Finish crawl ID {crawl_id}: {crawl_response} reports"
    )
