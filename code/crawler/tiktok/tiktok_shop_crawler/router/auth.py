import logging
from typing import Dict

from fastapi import APIRouter, Query  # type: ignore

from handler.auth import get_tokens
from handler.shop_apis import get_authorized_shop
from handler.mysql import set_crawl_info

router = APIRouter()


@router.get("/ingest/partner/tiktok/shop/auth")
async def get_auth(
    code: str = Query(..., description="Authorization code from TikTok Shop"),
    vada_uid: str = Query(..., description="Vada UID requesting the authorization"),
):
    try:
        # Step 1: Exchange auth code for tokens
        tokens = await get_tokens(code)
        logging.info(
            f"Access Token: {tokens['access_token']}, Refresh Token: {tokens['refresh_token']}, Seller: {tokens['seller_name']}"
        )

        # Step 2: Get authorized shop information
        shop_info = await get_authorized_shop(tokens["access_token"])

        index_name = f"data_tiktokshop_{shop_info['id']}"
        friendly_index_name = f"Tiktok Shop - {shop_info["name"]}"

        # Step 3: Set crawl info in MySQL
        await set_crawl_info(
            account_id=shop_info["id"],
            account_name=shop_info["name"],
            vada_uid=vada_uid,
            index_name=index_name,
            crawl_type="tiktok_shop",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            crawl_interval=120,  # 2 hours
        )

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
