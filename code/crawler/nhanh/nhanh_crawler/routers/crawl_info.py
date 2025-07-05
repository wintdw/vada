from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError

from tools import get_logger
from models import CrawlInfo, CrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.post("/v1/crawl/info", response_model=CrawlInfoResponse, tags=["CrawlInfo"])
async def post_crawl_info(crawl_info: CrawlInfo):
    from repositories import insert_crawl_info

    try:
        crawl_info = await insert_crawl_info(crawl_info)
    except IntegrityError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=409,
            detail="Conflict"
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(crawl_info)
    return CrawlInfoResponse(
        status=201,
        message="Created",
        data=crawl_info
    )

@router.get("/v1/crawl/{crawl_id}/info", response_model=CrawlInfoResponse, tags=["CrawlInfo"])
async def get_crawl_info_by_crawl_id(crawl_id: str):
    from repositories import select_crawl_info_by_crawl_id

    try:
        crawl_info = await select_crawl_info_by_crawl_id(crawl_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if crawl_info is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    else:
        logger.info(crawl_info)
        return CrawlInfoResponse(
            status=200,
            message="Success",
            data=crawl_info
        )

@router.get("/v1/crawl/info", response_model=CrawlInfoResponse, tags=["CrawlInfo"])
async def get_crawl_info():
    from repositories import select_crawl_info

    try:
        crawl_info = await select_crawl_info()
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

@router.put("/v1/crawl/{crawl_id}/info", response_model=CrawlInfoResponse, tags=["CrawlInfo"])
async def put_crawl_info(crawl_id: str, crawl_info: CrawlInfo):
    from repositories import select_crawl_info_by_crawl_id, update_crawl_info

    try:
        crawl_info_selected = await select_crawl_info_by_crawl_id(crawl_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if crawl_info_selected is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    else:
        try:
            crawl_info = await update_crawl_info(crawl_id, crawl_info)
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

@router.delete("/v1/crawl/{crawl_id}/info", response_model=CrawlInfoResponse, response_model_exclude_none=True, tags=["CrawlInfo"])
async def delete_crawl_info(crawl_id: str):
    from repositories import remove_crawl_info_by_crawl_id

    try:
        row_count = await remove_crawl_info_by_crawl_id(crawl_id)
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
