import logging
from typing import Dict

from fastapi import APIRouter, Query  # type: ignore

from hander.auth import TikTokShopAuth
from hander.mysql import set_crawl_info

router = APIRouter()


@router.get("/ingest/partner/google/ad/auth")
async def get_auth(
    code: str = Query(..., description="Authorization code from TikTok Shop"),
    vada_uid: str = Query(..., description="Vada UID for tracking"),
):
    try:
        tts = TikTokShopAuth()

        # Step 2: Exchange auth code for tokens
        tokens = await tts.get_tokens(code)
        logging.info(
            f"Access Token: {tokens['access_token']}, Refresh Token: {tokens['refresh_token']}, Seller: {tokens['seller_name']}"
        )

        # Set crawl info in MySQL
        await set_crawl_info(
            account_id=tokens["seller_id"],
            account_email=,
            vada_uid=vada_uid,
            index_name="tiktok_shop",
            crawl_type="tiktok_shop",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
    except Exception as e:
        print(f"Error: {e}")
