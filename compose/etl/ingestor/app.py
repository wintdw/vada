import os
import json
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from confluent_kafka import Producer
from typing import Dict, List

import security

app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka.ilb.vadata.vn:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dev_input")
PRODUCER = Producer({"bootstrap.servers": KAFKA_BROKER_URL})


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


def delivery_report(err, msg):
    """Callback function called once the message is delivered or fails"""
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def process_msg(msg: str) -> Dict:
    """
    This function is for further processing the message input by client

    Args:
        msg (str): message from client, expected a str

    Raises:
        json.JSONDecodeError: if parse error, or no IndexName field present

    Returns:
        Dict: A json object, with __meta field
    """
    json_msg = json.loads(msg)

    if not isinstance(json_msg, dict):
        raise json.JSONDecodeError(
            "Expected a JSON object (dictionary)", doc=json_msg, pos=0
        )

    if "IndexName" not in json_msg:
        raise json.JSONDecodeError("Missing IndexName field", doc=json_msg, pos=0)

    # move IndexName to meta
    json_msg["__meta"] = {"index_name": json_msg["IndexName"]}
    ret_msg = remove_fields(json_msg, ["IndexName"])

    return ret_msg


def produce_msg(producer: Producer, json_msg: Dict):
    """
    Function to produce message to Kafka topic

    Args:
        producer (Producer): the Kafka Producer object
        json_msg (Dict): the dict to be produced
    """
    producer.produce(
        KAFKA_TOPIC,
        value=json.dumps(json_msg).encode("utf-8"),
        callback=delivery_report,
    )


@app.get("/health")
async def check_health():
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.post("/v1/jsonl")
async def process_jsonl(req: Request, jwt_token: Dict = Depends(security.verify_jwt)):
    """
    Accept JSONL data as a string and send each line to Kafka.
    """
    data = await req.body()
    data_str = data.decode("utf-8")
    lines = data_str.strip().splitlines()

    count = 0
    for line in lines:
        try:
            json_msg = process_msg(line)
            # update meta
            json_msg["__meta"]["clientip"] = req.client.host
            produce_msg(PRODUCER, json_msg)
            count += 1
        except json.JSONDecodeError as json_err:
            logging.error(f"Invalid JSON format: {line} - {json_err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format: {line} - {json_err}",
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"Exception: {e}\nTraceback: {error_trace}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    # Flush all message in the buffer
    PRODUCER.flush()

    return JSONResponse(
        content={"status": "success", "detail": f"{count} messages received"}
    )
