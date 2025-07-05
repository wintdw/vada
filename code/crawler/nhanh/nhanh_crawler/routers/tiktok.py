import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from tools import get_logger

from handlers import (
    crawl_tiktok_business
)

router = APIRouter()
logger = get_logger(__name__, logging.INFO)

@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(index_name: str, access_token: str, start_date: str, end_date: str):
    """
    Get tiktok business data
    """
    try:
        crawl_response = await crawl_tiktok_business(index_name, access_token, start_date, end_date)
        logger.info(crawl_response)
        return crawl_response
    except Exception as e:
        logger.error(f"Error in tiktok_business_get: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")