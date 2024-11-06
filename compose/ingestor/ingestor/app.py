import os
import json
import logging
from fastapi import FastAPI, HTTPException, Request
from confluent_kafka import Producer
from typing import Dict


app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

KAFKA_BROKER_URL = os.getenv('KAFKA_BROKER_URL', "kafka.ilb.vadata.vn:9092")
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', "dev_input") 
PRODUCER = Producer({
    'bootstrap.servers': KAFKA_BROKER_URL
})


def delivery_report(err, msg):
    """ Callback function called once the message is delivered or fails """
    if err is not None:
        logging.info(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def process_msg(msg: str) -> Dict:
    """
    Placeholder for further processing
    """
    json_msg = json.loads(msg)
    return json_msg


def produce_msg(producer: Producer, json_msg: Dict):
    producer.produce(
        KAFKA_TOPIC,
        value=json.dumps(json_msg).encode('utf-8'),
        callback=delivery_report
    )


@app.post("/jsonl")
async def process_jsonl(req: Request):
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
            raise HTTPException(status_code=400, detail=f"Invalid JSONL format: {line}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        # meta
        json_msg["__meta"] = {"clientip": req.client.host}
        produce_msg(PRODUCER, json_msg)
        count += 1

    # Flush all message in the buffer
    PRODUCER.flush()

    return {"status": "success", "message": f"{count} messages sent to Kafka"}