import logging

from handler.auth import refresh_tokens
from handler.mysql import set_crawl_info


async def scheduled_refresh_token(refresh_token: str, vada_uid: str, account_id: str):
    """Job to refresh the token"""
    try:
        logging.info("Refreshing token...")
        new_tokens = await refresh_tokens(refresh_token)
        logging.info(f"New tokens: {new_tokens}")
        # Save the new tokens (e.g., to a database or file)
        crawl_info = await set_crawl_info(
            account_id=account_id,
            vada_uid=vada_uid,
            access_token=new_tokens["access_token"],
            refresh_token=new_tokens["refresh_token"],
        )
        logging.info(f"Updated crawl info: {crawl_info}")
    except Exception as e:
        logging.error(f"Failed to refresh token: {e}")
