from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError

from tools import get_logger
from models import CrawlHistory, CrawlHistoryResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.post("/v1/crawl/history", response_model=CrawlHistoryResponse, tags=["Crawl"])
async def post_crawl_history(crawl_history: CrawlHistory):
    from repositories import insert_crawl_history

    try:
        crawl_history = await insert_crawl_history(crawl_history)
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
    logger.info(crawl_history)
    return CrawlHistoryResponse(
        status=201,
        message="Created",
        data=crawl_history
    )

@router.get("/v1/crawl/{crawl_id}/history", response_model=CrawlHistoryResponse, tags=["Crawl"])
async def get_crawl_history_by_crawl_id(crawl_id: str):
    from repositories import select_crawl_history_by_crawl_id

    try:
        crawl_history = await select_crawl_history_by_crawl_id(crawl_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if crawl_history is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    else:
        logger.info(crawl_history)
        return CrawlHistoryResponse(
            status=200,
            message="Success",
            data=crawl_history
        )

@router.get("/v1/crawl/history", response_model=CrawlHistoryResponse, tags=["Crawl"])
async def get_crawl_history():
    from repositories import select_crawl_history

    try:
        crawl_history = await select_crawl_history()
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(crawl_history)
    return CrawlHistoryResponse(
        status=200,
        message="Success",
        data=crawl_history
    )

@router.put("/v1/crawl/{crawl_id}/history", response_model=CrawlHistoryResponse, tags=["Crawl"])
async def put_crawl_history(crawl_id: str, crawl_history: CrawlHistory):
    from repositories import select_crawl_history_by_crawl_id, update_crawl_history

    try:
        crawl_history_selected = await select_crawl_history_by_crawl_id(crawl_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if crawl_history_selected is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    else:
        try:
            crawl_history = await update_crawl_history(crawl_id, crawl_history)
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error"
            )
        logger.info(crawl_history)
        return CrawlHistoryResponse(
            status=200,
            message="Success",
            data=crawl_history
        )

@router.delete("/v1/crawl/{crawl_id}/history", response_model=CrawlHistoryResponse, response_model_exclude_none=True, tags=["Crawl"])
async def delete_crawl_history(crawl_id: str):
    from repositories import remove_crawl_history

    try:
        row_count = await remove_crawl_history(crawl_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if row_count > 0:
        return CrawlHistoryResponse(
            status=200,
            message="Success"
        )
    else:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
