import logging
from typing import Dict

from fastapi import APIRouter, Query  # type: ignore

from hander.auth import get_tokens
from hander.shop_apis import get_authorized_shop
from hander.mysql import set_crawl_info

router = APIRouter()


@router.get("/ingest/partner/google/ad/auth")
async def get_auth(
    code: str = Query(..., description="Authorization code from TikTok Shop"),
    vada_uid: str = Query(..., description="Vada UID for tracking"),
):
    try:

        # Step 2: Exchange auth code for tokens
        tokens = await get_tokens(code)
        logging.info(
            f"Access Token: {tokens['access_token']}, Refresh Token: {tokens['refresh_token']}, Seller: {tokens['seller_name']}"
        )

        # Step 3: Get authorized shop information
        shop_info = await get_authorized_shop(tokens["access_token"])

        # Set crawl info in MySQL
        await set_crawl_info(
            account_id=shop_info["id"],
            account_email=shop_info["name"],
            vada_uid=vada_uid,
            index_name=f"data_tiktokshop_{shop_info["id"]}",
            crawl_type="tiktok_shop",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

        friendly_index_name = f"Tiktok Shop - {shop_info["name"]}"

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
