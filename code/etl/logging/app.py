# pylint: disable=import-error,wrong-import-position

"""
This module is for processing jsonl and pushing to ES index
"""

import logging
import traceback
import asyncio
import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException, status, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from concurrent.futures import ThreadPoolExecutor

from etl.libs.processor import get_es_processor
from libs.connectors.async_es import AsyncESProcessor


app = FastAPI()
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Create a separate thread pool for health checks
health_check_executor = ThreadPoolExecutor(max_workers=1)


# This functions is for running health check in another threadpool worker
# so it's not blocked by the main thread
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


@app.get("/health")
async def check_health(es_processor: AsyncESProcessor = Depends(get_es_processor)):
    """Check the health of the Elasticsearch cluster."""
    response = await asyncio.get_event_loop().run_in_executor(
        health_check_executor, check_health_sync, es_processor
    )

    if response["status"] >= 400:
        logging.error(response["detail"])
        raise HTTPException(status_code=response["status"])

    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.post("/v1/logs")
async def capture_logs(
    request: Request, es_processor: AsyncESProcessor = Depends(get_es_processor)
) -> JSONResponse:
    """
    Process and store logs in Elasticsearch.

    Args:
        request (Request): The incoming request containing logs
        es_processor (AsyncESProcessor): Elasticsearch processor dependency

    Returns:
        JSONResponse: Processing result with status and details

    Raises:
        HTTPException: For invalid input or processing errors
    """
    MAX_BATCH_SIZE = 1000
    # Get environment from env var, default to 'development'
    APP_ENV = os.getenv("APP_ENV")

    try:
        data = await request.json()

        if not data or "logs" not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body must contain 'logs' field",
            )

        logs = data["logs"]
        if not isinstance(logs, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="'logs' must be an array",
            )

        if len(logs) > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE}",
            )

        # Add environment and timestamp to each log entry
        current_timestamp = datetime.now(timezone.utc).isoformat()
        enriched_logs = []
        for log in logs:
            if not isinstance(log, dict):
                log = {"message": str(log)}

            log.update(
                {
                    "environment": APP_ENV,
                    "@timestamp": log.get("@timestamp", current_timestamp),
                }
            )
            enriched_logs.append(log)

        # Create index name with date suffix
        current_date = datetime.now(timezone.utc).strftime("%Y.%m.%d")
        index_name = f"logs-{current_date}"

        # Use bulk indexing with enriched logs
        response = await es_processor.bulk_index_docs(index_name, enriched_logs)

        if response["status"] not in {200, 201}:
            logging.error("Failed to index documents: %s", response["detail"])
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response["detail"],
            )

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Successfully processed {len(logs)} log entries",
                "detail": response["detail"],
                "index": index_name,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    finally:
        await es_processor.close()
