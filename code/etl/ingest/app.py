# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import logging
from typing import Dict
from fastapi import FastAPI, Request, Depends, HTTPException, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

# custom libs
from libs.security.jwt import verify_jwt
from libs.connectors.async_es import AsyncESProcessor
from libs.connectors.async_kafka import AsyncKafkaProcessor
from libs.connectors.mappings import MappingsClient

from etl.libs.processor import (
    get_kafka_processor,
    get_es_processor,
    get_mappings_client,
)
from .process_jsonl import process_jsonl

app = FastAPI()
# asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

APP_ENV = os.getenv("APP_ENV")


@app.get("/health")
async def check_health(
    es_processor: AsyncESProcessor = Depends(get_es_processor),
    mappings_client: MappingsClient = Depends(get_mappings_client),
):
    """Check the health of the Elasticsearch cluster and Mappings service."""
    try:
        es_response = await es_processor.check_health()
        mappings_response = await mappings_client.check_health()
    finally:
        await es_processor.close()

    if es_response["status"] < 400 and mappings_response["status"] < 400:
        return JSONResponse(
            content={
                "status": "success",
                "es": "available",
                "mappings": "available",
            }
        )

    if es_response["status"] >= 400:
        logging.error(es_response["detail"])
    if mappings_response["status"] >= 400:
        logging.error(mappings_response["detail"])

    raise HTTPException(
        status_code=max(es_response["status"], mappings_response["status"]),
        detail="Downstream services are unavailable!",
    )


@app.post("/v1/jsonl")
async def handle_jsonl_req(
    req: Request,
    jwt_dict: Dict = Depends(verify_jwt),
    kafka_processor: AsyncKafkaProcessor = Depends(get_kafka_processor),
    es_processor: AsyncESProcessor = Depends(get_es_processor),
    mappings_client: MappingsClient = Depends(get_mappings_client),
):
    """
    Accept JSONL data as a string and send each line to Kafka.
    """
    data = await req.body()

    if not data or len(data) <= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Request empty"
        )

    data_str = data.decode("utf-8")
    lines = data_str.strip().splitlines()

    user_id = jwt_dict.get("id")

    try:
        response = await process_jsonl(
            APP_ENV, lines, user_id, kafka_processor, es_processor, mappings_client
        )
    except RuntimeError as run_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(run_err)
        )
    finally:
        await kafka_processor.close()
        await es_processor.close()

    return JSONResponse(content=response)
