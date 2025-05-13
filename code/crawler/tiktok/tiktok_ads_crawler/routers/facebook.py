import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from tools import get_logger

from services import (
    facebook_get_ads
)

router = APIRouter()
logger = get_logger(__name__, logging.INFO)

@router.get("/v1/facebook/get/", tags=["Facebook"])
async def facebook_get():
    """
    Get facebook data
    """
    try:
        crawl_response = await facebook_get_ads()
        logger.info(crawl_response)
        return crawl_response
    except Exception as e:
        logger.error(f"Error in facebook_get: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")