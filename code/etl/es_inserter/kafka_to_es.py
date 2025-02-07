# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from .async_proc import AsyncProcessor


APP_ENV = os.getenv("APP_ENV", "dev")

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

MAPPINGS_BASEURL = os.getenv("MAPPINGS_BASEURL", "http://mappings.internal.vadata.vn")


app = FastAPI()
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().setLevel(logging.INFO)


es_conf_dict = {"url": ELASTIC_URL, "user": ELASTIC_USER, "passwd": ELASTIC_PASSWD}
processor = AsyncProcessor(KAFKA_BROKER_URL, es_conf_dict, MAPPINGS_BASEURL)


@app.get("/health")
async def check_health() -> JSONResponse:
    """
    Health check function

    Returns:
        JSONResponse: Return 200 when service is available
    """

    response = await processor.es.check_health()
    if response["status"] < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    logging.error(response["json"])
    raise HTTPException(status_code=response["status"])


@app.on_event("startup")
async def background():
    """
    This function runs in the background, constantly monitors Kafka topics to consume, process,
    then produce to ES topic
    """

    asyncio.create_task(
        # example pattern "dev.csv_dw_csv"
        processor.consume_then_produce(rf"{APP_ENV}\..*csv_", "es_inserter_group")
    )
