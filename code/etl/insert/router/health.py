import os
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
def check_health_sync():
    """Check the health of the Elasticsearch cluster synchronously."""
    logging.debug("Health check process started (PID: %d)", os.getpid())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    es_processor = get_es_processor()
    try:
        response = loop.run_until_complete(es_processor.check_health())
    finally:
        loop.run_until_complete(es_processor.close())
        loop.close()
    return response


@router.get("/health")
async def check_health():
    """Check the health of the Elasticsearch cluster."""
    try:
        response = await asyncio.get_running_loop().run_in_executor(
            health_check_executor, check_health_sync
        )
    except Exception as e:
        logging.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")

    if response["status"] >= 400:
        logging.error(response["detail"])
        raise HTTPException(status_code=response["status"])

    return JSONResponse(content={"status": "success", "detail": "Service Available"})
