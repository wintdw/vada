import logging
from typing import Dict

from handler.auth import refresh_tokens, check_days_left_to_expiry
from handler.mysql import update_crawl_token

TOKEN_REFRESH_THRESHOLD_DAYS = 1


async def scheduled_refresh_token(
    crawl_id: str,
    refresh_token: str,
    access_token_expiry: int,
    refresh_token_expiry: int,
) -> Dict:
    """Job to refresh the token if it's close to expiry"""
    try:
        access_days_left = check_days_left_to_expiry(access_token_expiry)
        refresh_days_left = check_days_left_to_expiry(refresh_token_expiry)

        logging.info(
            f"Crawl ID {crawl_id}: access token expiry: {access_days_left}d, refresh token expiry: {refresh_days_left}d"
        )

        if (
            access_days_left <= TOKEN_REFRESH_THRESHOLD_DAYS
            or refresh_days_left <= TOKEN_REFRESH_THRESHOLD_DAYS
        ):
            logging.info("Refreshing token...")
            new_tokens = await refresh_tokens(refresh_token)

            # Save the new tokens
            crawl_info = await update_crawl_token(
                crawl_id=crawl_id,
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens["refresh_token"],
                access_token_expiry=new_tokens.get("access_token_expire_in", 0),
                refresh_token_expiry=new_tokens.get("refresh_token_expire_in", 0),
            )
            logging.info(f"Updated crawl info: {crawl_info}")

            return new_tokens
        else:
            return {"refresh_token": refresh_token}
    except Exception as e:
        logging.error(f"Failed to refresh token: {e}", exc_info=True)
        return {}
