import logging

from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore

from model.setting import settings
from model.index_mappings import index_mappings_data
from repository.crawl_info import set_crawl_info
from service.info import tiktok_biz_get_user_info
from service.oauth import tiktok_biz_get_access_token

router = APIRouter()


@router.get("/ingest/partner/tiktok/ad/callback", tags=["Connector"])
async def ingest_partner_tiktok_ad_callback(auth_code: str, state: str):
    try:
        access_token_response = await tiktok_biz_get_access_token(auth_code=auth_code)
        if not access_token_response:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        access_token = access_token_response["access_token"]

        user_info = await tiktok_biz_get_user_info(access_token=access_token)
        logging.info(user_info)

        account_id = user_info["core_user_id"]
        account_name = user_info["display_name"]
        index_name = f"data_tiktokad_{account_id}"
        friendly_index_name = f"Tiktok Ads - {account_name}"

        crawl_info = await set_crawl_info(
            account_id=account_id,
            vada_uid=state,
            account_name=account_name,
            index_name=index_name,
            access_token=access_token,
            crawl_interval=240,
        )
        logging.info(crawl_info)

        return RedirectResponse(
            url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={account_id}&account_name={account_name}&index_name={index_name}&friendly_index_name={friendly_index_name}"
        )
    except Exception as e:
        logging.error(f"Error during TikTok Ads callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/ingest/partner/tiktok/ad/auth", tags=["Connector"])
async def ingest_partner_tiktok_ad_auth(vada_uid: str):
    return RedirectResponse(
        url=f"https://business-api.tiktok.com/portal/auth?app_id={settings.TIKTOK_BIZ_APP_ID}&state={vada_uid}&redirect_uri={settings.TIKTOK_BIZ_REDIRECT_URI}"
    )


@router.get("/ingest/partner/tiktok/ad/config", tags=["Connector"])
async def ingest_partner_tiktok_ad_config():
    return {"mappings": index_mappings_data["mappings"]}
