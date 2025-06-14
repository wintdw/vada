import logging
from typing import Dict

from fastapi import APIRouter, Query  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore

from model.setting import settings
from handler.auth import get_tokens
from handler.shop_apis import get_authorized_shop
from handler.mysql import set_crawl_info

router = APIRouter()


@router.get("/ingest/partner/tiktok/shop/auth")
async def get_auth_url(
    vada_uid: str = Query(..., description="Vada UID requesting the authorization")
) -> RedirectResponse:
    """
    Generate and return a TikTok Shop OAuth authorization URL.
    The user will be redirected to this URL to authorize the application.
    """
    auth_url = settings.TIKTOK_SHOP_AUTH_LINK + "&state=" + vada_uid
    logging.info(f"Generated TikTok Shop Auth URL: {auth_url}")

    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/ingest/partner/tiktok/shop/callback")
async def get_auth(
    code: str = Query(..., description="Authorization code from TikTok Shop"),
    state: str = Query(..., description="Vada UID requesting the authorization"),
) -> RedirectResponse:
    try:
        # Step 1: Exchange auth code for tokens
        tokens = await get_tokens(code)
        logging.info(
            f"Access Token: {tokens['access_token']}, Refresh Token: {tokens['refresh_token']}, Seller: {tokens['seller_name']}"
        )

        # Step 2: Get authorized shop information
        shop_info = await get_authorized_shop(tokens["access_token"])

        account_id = shop_info["id"]
        account_name = shop_info["name"]
        index_name = f"data_tiktokshop_{shop_info['id']}"
        friendly_index_name = f"Tiktok Shop - {shop_info["name"]}"

        # Step 3: Set crawl info in MySQL
        await set_crawl_info(
            account_id=account_id,
            account_name=account_name,
            vada_uid=state,
            index_name=index_name,
            crawl_type="tiktok_shop",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            crawl_interval=240,  # 2 hours
        )

        fe_redirect_url = f"{settings.TIKTOK_SHOP_AUTH_CALLBACK}?account_id={account_id}&account_name={account_name}&index_name={index_name}&friendly_index_name={friendly_index_name}"
        return RedirectResponse(url=fe_redirect_url, status_code=302)

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
