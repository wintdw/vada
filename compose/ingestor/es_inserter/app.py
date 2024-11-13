import os
import json
import hashlib
import logging
import traceback
from aiohttp import ClientSession, ClientResponse, BasicAuth
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from confluent_kafka import Consumer
from typing import Dict, List


app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka.ilb.vadata.vn:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dev_input")
CONSUMER = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER_URL,
        "group.id": "es_inserter_group",
        "auto.offset.reset": "earliest",
    }
)
CONSUMER.subscribe([KAFKA_TOPIC])


ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r") as file:
        ELASTIC_PASSWD = file.read().strip()


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


async def send_to_es(index_name: str, doc_id: str, msg: Dict) -> ClientResponse:
    es_user = ELASTIC_USER
    es_pass = ELASTIC_PASSWD
    es_url = f"{ELASTIC_URL}/{index_name}/_doc/{doc_id}"

    async with ClientSession() as session:
        async with session.put(
            es_url, json=msg, auth=BasicAuth(es_user, es_pass)
        ) as response:
            logging.debug(f"Index: {index_name}")
            if response.status == 201:
                logging.debug("Document created successfully")
            elif response.status == 200:
                logging.debug("Document updated successfully")
            else:
                logging.error(
                    f"Failed to send data to Elasticsearch. Status code: {response.status}"
                )
                logging.error(await response.text())

            response.raise_for_status()

    return response


async def check_es_health() -> ClientResponse:
    es_user = ELASTIC_USER
    es_pass = ELASTIC_PASSWD
    es_url = f"{ELASTIC_URL}/_cluster/health"

    async with ClientSession() as session:
        async with session.get(es_url, auth=BasicAuth(es_user, es_pass)) as response:
            if response.status == 200:
                health_info = await response.json()
            else:
                logging.error(
                    f"Failed to get health info: {response.status} - {await response.text()}"
                )

    return response


@app.get("/health")
async def check_health():
    response = await check_es_health()

    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": f"{response.text}"},
        )


# This function can deal with duplicate messages
@app.post("/jsonl")
async def receive_jsonl(request: Request):
    try:
        body = await request.body()
        json_lines = body.decode("utf-8").splitlines()

        count = 0
        for line in json_lines:
            event = json.loads(line)
            # Check for required index_name
            if not event["index_name"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Missing index_name"
                )

            index_name = event["index_name"]
            doc = remove_fields(event, ["index_name", "__meta"])
            doc_id = generate_docid(doc)
            logging.debug(doc)

            response = await send_to_es(index_name, doc_id, doc)
            if response.status not in {200, 201}:
                raise HTTPException(status_code=response.status, detail=response.text())

            count += 1

        return JSONResponse(
            content={
                "status": "success",
                "detail": f"{count} messages successfully written",
            }
        )

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Exception: {e}\nTraceback: {error_trace}")
        return JSONResponse(
            content={"detail": "Internal Error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def consume_msg(consumer: Consumer, poll_timeout: float = 3.0) -> Dict:
    msg = consumer.poll(poll_timeout)
    logging.debug(f"Polling: {msg}")

    if msg is None:
        return {}

    return json.loads(msg.value().decode("utf-8"))


def process_msg(msg: Dict) -> Dict:
    """
    Placeholder for processing the message.
    Currently does nothing and just returns the input.
    """
    return msg


# Flow: consume from kafka -> process -> send to es
async def background_task():
    try:
        while True:
            input_msg = consume_msg(CONSUMER)
            output_msg = process_msg(input_msg)

            index_name = output_msg["index_name"]
            doc = remove_fields(output_msg, ["index_name", "__meta"])
            doc_id = generate_docid(doc)
            logging.debug(doc)

            await send_to_es(index_name, doc_id, doc)
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Exception: {e}\nTraceback: {error_trace}")
    finally:
        CONSUMER.close()


@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(background_task())
