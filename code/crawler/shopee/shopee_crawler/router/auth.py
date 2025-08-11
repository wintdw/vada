import logging

from fastapi import APIRouter, Query  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore

from model.setting import settings
from handler.shop_apis import get_authorized_shop
from handler.mysql import set_crawl_info

from utils import generate_shopee_auth_url, get_access_token

router = APIRouter()


@router.get("/ingest/partner/shopee/auth")
async def get_auth_url(
    vada_uid: str = Query(..., description="Vada UID requesting the authorization")
) -> RedirectResponse:
    redirect_url = f"{settings.API_BASE_URL}/ingest/partner/shopee/callback?vada_uid={vada_uid}"

    custom_params = {
        "vada_uid": vada_uid,
    }
    auth_url = generate_shopee_auth_url(
        redirect_url=redirect_url,
        custom_redirect_params=custom_params,
        sandbox=True
    )
    logging.info(f"Generated Shopee Auth : {auth_url}")
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/ingest/partner/shopee/callback")
async def get_auth(
    code: str = Query(..., description="Authorization code from TikTok Shop"),
    shop_id: int = Query(..., description="Shop Id from TikTok Shop"),
    vada_uid: str = Query(..., description="Vada UID requesting the authorization"),
) -> RedirectResponse:
    logging.info(
            f"Code: {code}"
        ) 
    try:
        tokens = await get_access_token(code, shop_id)
        logging.info(
            f"Access Token: {tokens['access_token']}, Refresh Token: {tokens['refresh_token']}"
        )
        shop_info = await get_authorized_shop(
            tokens["access_token"],
            shop_id
        )

        logging.info(
            f"Shoping: {shop_info}"
        )
        
        account_id = shop_id
        account_name = shop_info["shop_name"]
        index_name = f"data_shopee_shop_{account_id}"
        friendly_index_name = f"Shopee - {account_id}"
        
    
        # Step 3: Set crawl info in MySQL
        await set_crawl_info(
            account_id=account_id,
            account_name=account_name,
            vada_uid=vada_uid,
            index_name=index_name,
            crawl_type="shopee_shop",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            crawl_interval=240,  # 2 hours
        )

        fe_redirect_url = f"{settings.SHOPEE_SHOP_AUTH_CALLBACK}?account_id={account_id}&account_name={account_name}&index_name={index_name}&friendly_index_name={friendly_index_name}&vada_uid={vada_uid}"
        return RedirectResponse(url=fe_redirect_url, status_code=302)

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
