from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

router = APIRouter()
logger = get_logger(__name__, 20)


@router.get("/ingest/partner/tiktok/ad/callback", tags=["Connector"])
async def ingest_partner_tiktok_ad_callback(auth_code: str, state: str):

    from repositories import upsert_crawl_info
    from models import CrawlInfo
    from services import (
        tiktok_biz_get_access_token,
        tiktok_biz_get_user_info,
    )

    try:
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        user_info = await tiktok_biz_get_user_info(
            access_token=access_token.get("access_token", "")
        )
        logger.info(user_info)

        crawl_info = await upsert_crawl_info(
            CrawlInfo(
                account_id=user_info["core_user_id"],
                account_name=user_info["display_name"],
                vada_uid=state,
                access_token=access_token.get("access_token"),
                index_name=f"data_tiktokad_{user_info['core_user_id']}",
                crawl_type="tiktok_business_ads",
            )
        )
        logger.info(crawl_info)

        encoded_friendly_name = urlencode(
            {"friendly_index_name": f"Tiktok Ads - {crawl_info.account_name}"}
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return RedirectResponse(
        url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={user_info['core_user_id']}&account_name={crawl_info.account_name}&index_name={crawl_info.index_name}&{encoded_friendly_name}"
    )


@router.get("/ingest/partner/tiktok/ad/auth", tags=["Connector"])
async def ingest_partner_tiktok_ad_auth(vada_uid: str):
    return RedirectResponse(
        url=f"https://business-api.tiktok.com/portal/auth?app_id=7480814660439146497&state={vada_uid}&redirect_uri={settings.TIKTOK_BIZ_REDIRECT_URI}"
    )


@router.get("/ingest/partner/tiktok/ad/config", tags=["Connector"])
async def ingest_partner_tiktok_ad_config():
    from models.index_mappings import index_mappings_data

    return {"mappings": index_mappings_data["mappings"]}
