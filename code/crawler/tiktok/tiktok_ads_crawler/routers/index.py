from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError

from tools import get_logger
from models import CrawlInfo, CrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.delete("/v1/index/{index_name}", response_model=CrawlInfoResponse, response_model_exclude_none=True, tags=["Index"])
async def delete_crawl_info_by_index_name(index_name: str):
    from repositories import remove_crawl_info_by_index_name

    try:
        row_count = await remove_crawl_info_by_index_name(index_name)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if row_count > 0:
        return CrawlInfoResponse(
            status=200,
            message="Success"
        )
    else:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
