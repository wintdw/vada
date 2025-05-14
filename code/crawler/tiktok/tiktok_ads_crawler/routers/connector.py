from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError
from datetime import datetime

from tools import get_logger
from models import CrawlInfo, CrawlInfoResponse
from services import (
    tiktok_biz_get_access_token
)
from fastapi.responses import RedirectResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/connector/tiktok/ads", response_model=CrawlInfoResponse, tags=["Connector"])
async def get_connector_tiktok_auth(auth_code: str, user_id: str = "tiktok_ads_test"):
    from repositories import insert_crawl_info

    try:
        user_info = await tiktok_biz_get_user_info(access_token=auth_code)
        print(user_info)
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        
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
    return RedirectResponse(url=f"https://qa.vadata.vn/callback.html?crawl_id={crawl_info.crawl_id}")

@router.get("/connector/tiktok/test", response_model=CrawlInfoResponse, tags=["Connector"])
async def get_connector_tiktok_auth1():
    return RedirectResponse(url="https://business-api.tiktok.com/portal/auth?app_id=7480814660439146497&state=your_custom_params&redirect_uri=https%3A%2F%2Fcrawl-dev.vadata.vn%2Fconnector%2Ftiktok%2Fads")