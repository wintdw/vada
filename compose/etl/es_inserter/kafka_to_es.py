import os
import fastapi
import logging
import traceback
import asyncio
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import utils

app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
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


class AsyncKafkaProcessor:
    def __init__(
        self,
        kafka_broker_url: str,
        kafka_topic: str,
        elastic_url: str,
        elastic_user: str,
        elastic_passwd: str,
    ):
        self.consumer = AIOKafkaConsumer(
            kafka_topic,
            loop=asyncio.get_event_loop(),  # Provide the event loop explicitly
            bootstrap_servers=kafka_broker_url,
            group_id="es_inserter_group",
            auto_offset_reset="earliest",
        )
        self.elastic_url = elastic_url
        self.elastic_user = elastic_user
        self.elastic_passwd = elastic_passwd

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self):
        try:
            # Ensure the consumer is started before polling for messages
            await self.consumer.start()

            while True:
                input_msg = await utils.consume_msg(self.consumer)
                # If no message retrieved
                if not input_msg:
                    continue

                output_msg = utils.process_msg(input_msg)

                # Attempt to get index_name from __meta, and continue if not found
                index_name = output_msg.get("__meta", {}).get("index_name")
                if not index_name:
                    continue

                doc = utils.remove_fields(output_msg, ["__meta"])
                doc_id = utils.generate_docid(doc)
                logging.info(doc)

                await utils.send_to_es(
                    self.elastic_url,
                    self.elastic_user,
                    self.elastic_passwd,
                    index_name,
                    doc_id,
                    doc,
                )
        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"Exception: {e}\nTraceback: {error_trace}")
        finally:
            # Ensure the consumer is stopped gracefully
            await self.consumer.stop()


@app.get("/health")
async def check_health():
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.on_event("startup")
async def background():
    runner = AsyncKafkaProcessor(
        KAFKA_BROKER_URL, KAFKA_TOPIC, ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD
    )
    asyncio.create_task(runner.consume_then_produce())
