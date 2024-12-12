# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import logging
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from es_inserter.async_proc import AsyncProcessor


ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka.ilb.vadata.vn:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dev_input")

MONGO_DB = os.getenv("MONGO_DB", "vada")
MONGO_COLL = os.getenv("MONGO_COLL", "master_indices")
MONGO_URI = ""
mongo_uri_file = os.getenv("MONGO_URI_FILE", "")
if mongo_uri_file and os.path.isfile(mongo_uri_file):
    with open(mongo_uri_file, "r", encoding="utf-8") as file:
        MONGO_URI = file.read().strip()


app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@app.get("/health")
async def check_health() -> JSONResponse:
    """
    Health check function

    Returns:
        JSONResponse: Return 200 when service is available
    """
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.on_event("startup")
async def background():
    """
    This function runs in the background, constantly monitors Kafka topics to consume, process,
    then produce to ES topic
    """
    es_conf_dict = {"url": ELASTIC_URL, "user": ELASTIC_USER, "passwd": ELASTIC_PASSWD}
    processor = AsyncProcessor(KAFKA_BROKER_URL, es_conf_dict, MONGO_URI)

    asyncio.create_task(
        processor.consume_then_produce(KAFKA_TOPIC, "es_inserter_group")
    )
