import os
import json
import logging
from fastapi import FastAPI, HTTPException, Request, Depends, status
from confluent_kafka import Producer
from typing import Dict

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


def delivery_report(err, msg):
    """Callback function called once the message is delivered or fails"""
    if err is not None:
        logging.info(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def process_msg(msg: str) -> Dict:
    """
    Placeholder for further processing
    """
    try:
        json_msg = json.loads(msg)
        if not isinstance(json_msg, dict):
            raise ValueError(f"Expected a JSON object (dictionary), but got a different JSON type: {msg}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def produce_msg(producer: Producer, json_msg: Dict):
    """
    Function to produce message to Kafka topic

    Args:
        producer (Producer): _description_
        json_msg (Dict): _description_
    """
    producer.produce(
        KAFKA_TOPIC,
        value=json.dumps(json_msg).encode("utf-8"),
        callback=delivery_report,
    )


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
        except json.JSONDecodeError:
            logging.error(f"Invalid JSONL format: {line}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSONL format: {line}",
            )
        except Exception as e:
            logging.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        # meta
        json_msg["__meta"] = {"clientip": req.client.host}
        produce_msg(PRODUCER, json_msg)
        count += 1

    # Flush all message in the buffer
    PRODUCER.flush()

    return {"status": "success", "message": f"{count} messages sent to Kafka"}
