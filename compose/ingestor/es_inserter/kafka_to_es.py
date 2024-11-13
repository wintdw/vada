import os
import fastapi
import logging
import traceback
from confluent_kafka import Consumer
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import utils

app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r") as file:
        ELASTIC_PASSWD = file.read().strip()

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


@app.get("/health")
async def check_health():
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


# Flow: consume from kafka -> process -> send to es
@app.on_event("startup")
async def consume_then_produce():
    try:
        while True:
            input_msg = consume_msg(CONSUMER)
            output_msg = process_msg(input_msg)

            # if message is not valid (no index_name), do not process
            if "index_name" in output_msg:
                index_name = output_msg["index_name"]
            else:
                continue

            doc = utils.remove_fields(output_msg, ["index_name", "__meta"])
            doc_id = utils.generate_docid(doc)
            logging.debug(doc)

            await utils.send_to_es(
                ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD, index_name, doc_id, doc
            )
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Exception: {e}\nTraceback: {error_trace}")
    finally:
        CONSUMER.close()
