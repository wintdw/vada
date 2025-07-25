import logging
from datetime import datetime, timedelta

from handler.report import fetch_google_reports
from handler.mysql import update_crawl_time


async def crawl_new_client(
    crawl_id: str,
    refresh_token: str,
    index_name: str,
    vada_uid: str,
    account_name: str,
    crawl_interval: int,
):
    now = datetime.now()
    start_date = now - timedelta(days=365)
    chunk = timedelta(days=30)
    current_start = start_date

    try:
        logging.info(
            f"[Scheduler] Starting initial crawl for {account_name} from {current_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
        )
        # Crawl 1 year of data in 12 monthly jobs
        while current_start < now:
            current_end = min(current_start + chunk, now)
            await fetch_google_reports(
                refresh_token=refresh_token,
                start_date=current_start.strftime("%Y-%m-%d"),
                end_date=current_end.strftime("%Y-%m-%d"),
                persist=True,
                index_name=index_name,
                vada_uid=vada_uid,
                account_name=account_name,
            )
            logging.info(
                f"[Scheduler] Initial crawl for {account_name} from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')} completed."
            )
            current_start = current_end

        # Update crawl time after all chunks are done
        await update_crawl_time(crawl_id, crawl_interval)
    except Exception as e:
        logging.error(
            f"[Scheduler] Error during initial crawl for {account_name}: {str(e)}",
            exc_info=True,
        )


async def crawl_daily(
    crawl_id: str,
    refresh_token: str,
    index_name: str,
    vada_uid: str,
    account_name: str,
    crawl_interval: int,
):
    try:
        now = datetime.now()
        start_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        logging.info(
            f"[Scheduler] Starting daily crawl for {account_name} from {start_date} to {end_date}"
        )
        await fetch_google_reports(
            refresh_token=refresh_token,
            start_date=start_date,
            end_date=end_date,
            persist=True,
            index_name=index_name,
            vada_uid=vada_uid,
            account_name=account_name,
        )
        logging.info(f"[Scheduler] daily crawl for {account_name} completed.")

        await update_crawl_time(crawl_id, crawl_interval)
    except Exception as e:
        logging.error(
            f"[Scheduler] Error during daily crawl for {account_name}: {str(e)}",
            exc_info=True,
        )
