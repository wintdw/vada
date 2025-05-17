from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime

from tools import get_logger

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/tiktok/ad/callback", tags=["Connector"])
async def ingest_partner_tiktok_ad_callback(auth_code: str, user_id: str = "tiktok_ads_test"):
    from repositories import insert_crawl_info
    from models import CrawlInfo
    from services import (
        tiktok_biz_get_access_token,
        tiktok_biz_get_user_info,
    )
    try:
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        user_info = await tiktok_biz_get_user_info(access_token=access_token.get("access_token"))
        logger.info(user_info)
        
        crawl_info = await insert_crawl_info(CrawlInfo(
            access_token=access_token.get("access_token"),
            index_name=user_id,
            crawl_type="tikTok_business_ads",
            crawl_from_date=datetime.now(),
            crawl_to_date=datetime.now()
        ))
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(crawl_info)
    return RedirectResponse(url=f"https://qa.vadata.vn/callback.html?account_email={user_info["email"]}&index_name={crawl_info.index_name}")

@router.get("/ingest/partner/tiktok/ad/auth", tags=["Connector"])
async def ingest_partner_tiktok_ad_auth():
    return RedirectResponse(url="https://business-api.tiktok.com/portal/auth?app_id=7480814660439146497&state=your_custom_params&redirect_uri=https%3A%2F%2Fapi-dev.vadata.vn%2Fingest%2Fpartner%2Ftiktok%2Fad%2Fcallback")