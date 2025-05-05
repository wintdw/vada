from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError

from tools import get_logger
from models import CrawlInfo, CrawlInfoResponse
from services import (
    tiktok_biz_get_access_token
)

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/connector/tiktok/ads", response_model=CrawlInfoResponse, tags=["Connector"])
async def get_connector_tiktok_auth(auth_code: str, user_id: str = "tiktok_ads_test"):
    from repositories import insert_crawl_info

    try:
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        
        crawl_info = await insert_crawl_info(CrawlInfo(
            access_token=access_token.get("access_token"),
            index_name=user_id
        ))
        
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(crawl_info)
    return CrawlInfoResponse(
        status=200,
        message="Success",
        data=crawl_info
    )
