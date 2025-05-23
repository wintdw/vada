import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.insert.handler.processor import get_es_processor
from libs.connectors.async_es import AsyncESProcessor


router = APIRouter()
# Create a separate process pool for health checks
health_check_executor = ProcessPoolExecutor(max_workers=1)


# This function runs health check in another process
# so it's not blocked by the main process
def check_health_sync(es_processor: AsyncESProcessor):
    """Check the health of the Elasticsearch cluster synchronously."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(es_processor.check_health())
    finally:
        loop.run_until_complete(es_processor.close())
        loop.close()
    return response


@router.get("/health")
async def check_health():
    """Check the health of the Elasticsearch cluster."""
    es_processor: AsyncESProcessor = get_es_processor()

    response = await asyncio.get_event_loop().run_in_executor(
        health_check_executor, check_health_sync, es_processor
    )

    if response["status"] >= 400:
        logging.error(response["detail"])
        raise HTTPException(status_code=response["status"])

    return JSONResponse(content={"status": "success", "detail": "Service Available"})
