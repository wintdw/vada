# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import asyncio
import logging
import traceback
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, Depends, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

# custom libs
from etl.libs.vadadoc import VadaDocument
from libs.security.jwt import verify_jwt
from libs.connectors.async_kafka import AsyncKafkaProcessor
from libs.utils.es_field_types import determine_and_convert_es_field_types
from .dependencies import get_kafka_processor

app = FastAPI()
# asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

APP_ENV = os.getenv("APP_ENV", "dev")


@app.get("/health")
async def check_health() -> JSONResponse:
    """
    Health check url

    Returns:
        JSONResponse: HTTP 200 if ok
    """
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.post("/v1/jsonl")
async def process_jsonl(
    req: Request,
    jwt_dict: Dict = Depends(verify_jwt),
    kafka_processor: AsyncKafkaProcessor = Depends(get_kafka_processor),
):
    """
    Accept JSONL data as a string and send each line to Kafka.
    """
    data = await req.body()
    data_str = data.decode("utf-8")
    lines = data_str.strip().splitlines()

    # Reconstruct the list of json data
    successful_count = 0
    failed_count = 0
    json_docs = []
    failed_lines = []

    for line in lines:
        try:
            vada_doc = VadaDocument(line)
        except Exception as json_err:
            logging.error("Invalid JSON format: %s - %s", line, json_err)
            failed_lines.append({"line": line, "error": str(json_err)})
            failed_count += 1
        vada_doc.populate_ingestor_metadata()
        vada_doc.set_user_id(jwt_dict.get("id"))
        json_docs.append(vada_doc.get_doc())

    json_converted_docs = determine_and_convert_es_field_types(json_docs)
    try:
        # Start the producer
        await kafka_processor.create_producer()
        # Concurrently process messages
        tasks = []
        for json_doc in json_converted_docs:
            try:
                vada_doc = VadaDocument(json_doc)
                index_name = vada_doc.get_index_name()
                kafka_topic = f"{APP_ENV}.{index_name}"
                # Create task for producing the message
                tasks.append(kafka_processor.produce_message(kafka_topic, json_doc))
                successful_count += 1
            except Exception as e:
                error_trace = traceback.format_exc()
                logging.error("Error processing line: %s\n%s", json_doc, error_trace)
                failed_lines.append({"line": json_doc, "error": str(e)})
                failed_count += 1

        # Await all produce tasks
        await asyncio.gather(*tasks)

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Unexpected error: %s\n%s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    finally:
        await kafka_processor.close()

    logging.debug(f"{successful_count} messages received")

    if failed_count > 0:
        upload_status = "partial"
    else:
        upload_status = "success"

    # Response
    response = {
        "status": upload_status,
        "details": f"{successful_count} messages received, {failed_count} failed",
        "failures": failed_lines,
    }
    return JSONResponse(content=response)
