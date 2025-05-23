from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/tiktok/ad/callback", tags=["Connector"])
async def ingest_partner_tiktok_ad_callback(auth_code: str, state: str):
    from repositories import insert_crawl_info
    from models import CrawlInfo
    from services import (
        tiktok_biz_get_access_token,
        tiktok_biz_get_user_info,
        create_crm_mappings
    )
    from handlers import (
        crawl_tiktok_business
    )

    try:
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        user_info = await tiktok_biz_get_user_info(access_token=access_token.get("access_token"))
        logger.info(user_info)
        
        crawl_info = await insert_crawl_info(CrawlInfo(
            account_id=user_info["core_user_id"],
            account_email=user_info["email"],
            vada_uid=state,
            access_token=access_token.get("access_token"),
            index_name=f"data_tiktokad_default_{state}",
            crawl_type="tiktok_business_ads",
            crawl_from_date=datetime.now(),
            crawl_to_date=datetime.now()
        ))
        logger.info(crawl_info)

        crawl_status = await crawl_tiktok_business(
            index_name=crawl_info.index_name,
            access_token=access_token.get("access_token"),
            start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
        logger.info(crawl_status)

        mappings_response = await create_crm_mappings(
            index_name=crawl_info.index_name,
            vada_uid=state,
            account_email=user_info["email"],
        )
        logger.info(mappings_response)

        encoded_friendly_name = urlencode({"friendly_index_name": f"Tiktok Ads {user_info['email']}"})
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return RedirectResponse(url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={user_info["core_user_id"]}&account_email={user_info["email"]}&index_name={crawl_info.index_name}&{encoded_friendly_name}")

@router.get("/ingest/partner/tiktok/ad/auth", tags=["Connector"])
async def ingest_partner_tiktok_ad_auth(vada_uid: str):
    return RedirectResponse(url=f"https://business-api.tiktok.com/portal/auth?app_id=7480814660439146497&state={vada_uid}&redirect_uri=https%3A%2F%2Fapi-dev.vadata.vn%2Fingest%2Fpartner%2Ftiktok%2Fad%2Fcallback")