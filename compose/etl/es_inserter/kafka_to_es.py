import os
import logging
import asyncio
import fastapi
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from aiohttp import ClientResponse

from async_proc import AsyncProcessor


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

MONGO_DB = os.getenv("MONGO_DB", "vada")
MONGO_COLL = os.getenv("MONGO_COLL", "master_indices")
MONGO_URI = ""
mongo_uri_file = os.getenv("MONGO_URI_FILE", "")
if mongo_uri_file and os.path.isfile(mongo_uri_file):
    with open(mongo_uri_file, "r") as file:
        MONGO_URI = file.read().strip()


app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@app.get("/health")
async def check_health():
    response = await es_processor.check_es_health()

    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    else:
        logging.error(response.text)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.on_event("startup")
async def background():
    kafka_processor = AsyncKafkaProcessor(KAFKA_BROKER_URL)
    es_processor = AsyncESProcessor(ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD)
    mongo_processor = AsyncMongoProcessor(MONGO_URI)

    processor = AsyncProcessor(kafka_processor, es_processor, mongo_processor)

    asyncio.create_task(
        processor.consume_then_produce(KAFKA_TOPIC, "es_inserter_group")
    )
