import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from tools import get_logger

from services.nhanh import crawl_nhanh_data


router = APIRouter()
logger = get_logger(__name__, logging.INFO)

@router.get("/v1/nhanh/get/", tags=["nhanh"])
async def nhanh_get(index_name: str, business_id: str, access_token: str, start_date: str, end_date: str):
    try:
        crawl_response = await crawl_nhanh_data(
            index_name,
            business_id,
            access_token,
            start_date,
            end_date
        )
        logger.info(crawl_response)
        return crawl_response
    except Exception as e:
        logger.error(f"Error in nhanh_get: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")