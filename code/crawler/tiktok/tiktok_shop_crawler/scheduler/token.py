import logging
from typing import Dict

from handler.auth import refresh_tokens, check_days_left_to_expiry
from handler.crawl_info import update_crawl_token, get_crawl_info

TOKEN_REFRESH_THRESHOLD_DAYS = 1


async def refresh_token_scheduler(crawl_id: str) -> Dict:
    """Job to refresh the token if it's close to expiry"""
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    account_name = crawl_info[0]["account_name"]
    refresh_token = crawl_info[0]["refresh_token"]
    access_token_expiry = crawl_info[0]["access_token_expiry"]
    refresh_token_expiry = crawl_info[0]["refresh_token_expiry"]

    try:
        access_days_left = check_days_left_to_expiry(access_token_expiry)
        refresh_days_left = check_days_left_to_expiry(refresh_token_expiry)

        logging.info(
            f"[{account_name}] [Token] Access token expiry: {access_days_left}d, Refresh token expiry: {refresh_days_left}d"
        )

        if (
            access_days_left <= TOKEN_REFRESH_THRESHOLD_DAYS
            or refresh_days_left <= TOKEN_REFRESH_THRESHOLD_DAYS
        ):
            new_tokens = await refresh_tokens(refresh_token)

            # Save the new tokens
            crawl_info = await update_crawl_token(
                crawl_id=crawl_id,
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens["refresh_token"],
                access_token_expiry=new_tokens["access_token_expire_in"],
                refresh_token_expiry=new_tokens["refresh_token_expire_in"],
            )
            logging.info(f"[{account_name}] [Token] Updated crawl info: {crawl_info}")

            return new_tokens
        else:
            return {"refresh_token": refresh_token}
    except Exception as e:
        logging.error(
            f"[{account_name}] [Token] Failed to refresh tokens: {e}", exc_info=True
        )
        return {}
