# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.libs.processor import get_es_processor, get_kafka_processor
from libs.connectors.async_es import AsyncESProcessor
from .async_proc import AsyncProcessor


app = FastAPI()
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().setLevel(logging.INFO)


APP_ENV = os.getenv("APP_ENV")


@app.get("/health")
async def check_health(
    es_processor: AsyncESProcessor = Depends(get_es_processor),
) -> JSONResponse:
    """
    Health check function

    Returns:
        JSONResponse: Return 200 when service is available
    """

    response = await es_processor.check_health()
    if response["status"] < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    logging.error(response["detail"])
    raise HTTPException(status_code=response["status"])


@app.on_event("startup")
async def background(
    es_processor: AsyncESProcessor = Depends(get_es_processor),
    kafka_processor: AsyncESProcessor = Depends(get_kafka_processor),
):
    """
    This function runs in the background, constantly monitors Kafka topics to consume, process,
    then produce to ES topic
    """

    processor = AsyncProcessor(es_processor, kafka_processor)

    asyncio.create_task(
        # example pattern "dev.csv_dw_csv"
        processor.consume_then_produce(rf"{APP_ENV}\..*csv_", "es_inserter_group")
    )
