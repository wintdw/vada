import json
from fastapi import FastAPI, HTTPException, Request
from confluent_kafka import Producer
from typing import Dict


app = FastAPI()
KAFKA_BROKER_URL = "kafka.ilb.vadata.vn:9092"
KAFKA_TOPIC = "dev_input"
PRODUCER = Producer({
    'bootstrap.servers': KAFKA_BROKER_URL
})


def delivery_report(err, msg):
    """ Callback function called once the message is delivered or fails """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def process_msg(msg: str) -> Dict:
    """
    Placeholder for further processing
    """
    json_msg = json.loads(line)
    return json_msg


def produce_msg(producer: Producer, json_msg: Dict):
    producer.produce(
        KAFKA_TOPIC,
        value=json.dumps(json_msg).encode('utf-8'),
        callback=delivery_report
    )


@app.post("/jsonl")
async def send_jsonl(req: Request):
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
            produce_msg(PRODUCER, json_msg)
            count += 1
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail=f"Invalid JSONL format: {line}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Flush all message in the buffer
    PRODUCER.flush()

    return {"status": "success", "message": f"{count} messages sent to Kafka"}