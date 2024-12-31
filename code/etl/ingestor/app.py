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
import libs.utils
import libs.security
from libs.async_kafka import AsyncKafkaProcessor


app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka.ilb.vadata.vn:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dev_input")

kafka_processor = AsyncKafkaProcessor(KAFKA_BROKER_URL)


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
    req: Request, jwt_dict: Dict = Depends(libs.security.verify_jwt)
):
    """
    Accept JSONL data as a string and send each line to Kafka.
    """
    data = await req.body()
    data_str = data.decode("utf-8")
    lines = data_str.strip().splitlines()

    # Validate JWT
    user_id = jwt_dict.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in JWT",
        )

    # Reconstruct the list of json data
    successful_count = 0
    json_msgs = []
    failed_lines = []

    for line in lines:
        try:
            json_msg = libs.utils.process_msg(line)
            json_msgs.append(json_msg)
        except libs.utils.ValidationError as json_err:
            logging.error("Invalid JSON format: %s - %s", line, json_err)
            failed_lines.append({"line": line, "error": str(json_err)})

    json_converted_msgs = libs.utils.convert_dict_values(json_msgs)
    try:
        # Start the producer
        await kafka_processor.create_producer()
        # Concurrently process messages
        tasks = []
        for json_msg in json_converted_msgs:
            try:
                json_msg["__vada"]["user_id"] = user_id
                # Create task for producing the message
                tasks.append(kafka_processor.produce_message(KAFKA_TOPIC, json_msg))
                successful_count += 1
            except Exception as e:
                error_trace = traceback.format_exc()
                logging.error("Error processing line: %s\n%s", json_msg, error_trace)
                failed_lines.append({"line": json_msg, "error": str(e)})

        # Await all produce tasks
        await asyncio.gather(*tasks)

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Unexpected error: %s\n%s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    finally:
        await kafka_processor.close()

    logging.debug(f"{successful_count} messages received")
    # Response
    response = {
        "status": "success",
        "detail": f"{successful_count} messages received",
        "failed": failed_lines,
    }
    return JSONResponse(content=response)
