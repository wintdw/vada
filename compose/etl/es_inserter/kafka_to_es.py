import os
import fastapi
import logging
import traceback
import asyncio
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from aiohttp import ClientResponse

import utils
from async_es import AsyncESProcessor
from async_kafka import AsyncKafkaProcessor
from async_mongo import AsyncMongoProcessor


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
kafka_processor = AsyncKafkaProcessor(KAFKA_BROKER_URL)
es_processor = AsyncESProcessor(ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD)
mongo_processor = AsyncMongoProcessor(MONGO_URI)


class AsyncProcessor:
    def __init__(
        self,
        kafka: AsyncKafkaProcessor,
        es: AsyncESProcessor,
        mongo: AsyncMongoProcessor,
    ):
        self.kafka = kafka
        self.es = es
        self.mongo = mongo

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self):
        try:
            while True:
                input_msg = await self.kafka.consume_msg(
                    KAFKA_TOPIC, "es_inserter_group"
                )
                # If no message retrieved
                if not input_msg:
                    continue

                output_msg = await self.kafka.process_msg(input_msg)

                # Attempt to get index_name from __meta, and continue if not found
                index_name = output_msg.get("__meta", {}).get("index_name")
                if not index_name:
                    continue

                doc = utils.remove_fields(output_msg, ["__meta"])
                doc_id = utils.generate_docid(doc)
                logging.info(doc)

            # send to ES
            response = await self.es.send_to_es(index_name, doc_id, doc)
            if response.status not in {200, 201}:
                raise HTTPException(
                    status_code=response.status, detail=await response.text()
                )
        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"Exception: {e}\nTraceback: {error_trace}")
        finally:
            await self.kafka.close_consumer()

    # Set mapping if only mongo doesnt have mapping for the index
    async def set_mapping(
        self,
        index_name: str,
        mongo_db: str = "vada",
        mongo_coll: str = "master_indices",
    ):
        mongo_mapping = await self.mongo.find_document(
            mongo_db, mongo_coll, {"name": index_name}
        )
        es_mapping = await self.es.get_es_index_mapping(index_name)
        logging.info(mongo_mapping)
        logging.info(es_mapping)


@app.get("/health")
async def check_health():
    response = await es_processor.check_es_health()

    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": f"{response.text}"},
        )


@app.on_event("startup")
async def background():
    processor = AsyncProcessor(kafka_processor, es_processor, mongo_processor)
    await processor.set_mapping("demo_sale_data")
    asyncio.create_task(processor.consume_then_produce())
