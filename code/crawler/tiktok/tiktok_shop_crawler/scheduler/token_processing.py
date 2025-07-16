import logging

from handler.auth import refresh_tokens
from handler.mysql import update_crawl_token


async def scheduled_refresh_token(crawl_id: str, refresh_token: str):
    """Job to refresh the token"""
    try:
        logging.info("Refreshing token...")
        new_tokens = await refresh_tokens(refresh_token)

        # Save the new tokens
        crawl_info = await update_crawl_token(
            crawl_id=crawl_id,
            access_token=new_tokens["access_token"],
            refresh_token=new_tokens["refresh_token"],
        )
        logging.info(f"Updated crawl info: {crawl_info}")

    except Exception as e:
        logging.error(f"Failed to refresh token: {e}")
