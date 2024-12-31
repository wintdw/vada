# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import logging
import asyncio
from fastapi import FastAPI  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

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

CRM_BASEURL = os.getenv("CRM_BASEURL", "https://dev-crm-api.vadata.vn")
CRM_USER = ""
CRM_PASS = ""
passwd_file = os.getenv("CRM_PASSWD_FILE", "")
if passwd_file and os.path.isfile(passwd_file):
    with open(passwd_file, "r", encoding="utf-8") as file:
        content = file.read().strip()
        CRM_USER, CRM_PASS = content.split(maxsplit=1)


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
    crm_conf_dict = {
        "auth": {"username": CRM_USER, "password": CRM_PASS},
        "baseurl": CRM_BASEURL,
    }
    processor = AsyncProcessor(KAFKA_BROKER_URL, es_conf_dict, crm_conf_dict)

    asyncio.create_task(
        processor.consume_then_produce(KAFKA_TOPIC, "es_inserter_group")
    )
