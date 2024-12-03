import os
import json
import asyncio
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, List

import utils
import security
from async_kafka import AsyncKafkaProcessor

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
async def check_health():
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.post("/v1/jsonl")
async def process_jsonl(req: Request, jwt_dict: Dict = Depends(security.verify_jwt)):
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
    json_msgs = []
    for line in lines:
        try:
            json_msg = utils.process_msg(line)
            json_msgs.append(json_msg)
        except utils.ValidationError as json_err:
            logging.error(f"Invalid JSON format: {line} - {json_err}")
            failed_lines.append({"line": line, "error": str(json_err)})

    json_converted_msgs = utils.convert_dict_values(json_msgs)

    # Start producing to Kafka topic
    successful_count = 0
    failed_lines = []
    try:
        # Start the producer
        await kafka_processor.create_producer()
        # Concurrently process messages
        tasks = []
        for json_msg in json_converted_msgs:
            try:
                json_msg["__meta"]["user_id"] = user_id
                # Create task for producing the message
                tasks.append(kafka_processor.produce_message(KAFKA_TOPIC, json_msg))
                successful_count += 1
            except Exception:
                error_trace = traceback.format_exc()
                logging.error(f"Error processing line: {line}\nTraceback:{error_trace}")
                failed_lines.append({"line": line, "error": str(e)})

        # Await all produce tasks
        await asyncio.gather(*tasks)

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Unexpected error: {e}\nTraceback: {error_trace}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        await kafka_processor.close()

    # Response
    response = {
        "status": "success",
        "detail": f"{successful_count} messages received",
        "failed": failed_lines,
    }
    return JSONResponse(content=response)
