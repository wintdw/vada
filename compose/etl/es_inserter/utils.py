import json
import logging
import hashlib
from typing import Dict, List
from aiokafka import AIOKafkaConsumer
from aiohttp import ClientSession, ClientResponse, BasicAuth


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


async def consume_msg(consumer: AIOKafkaConsumer) -> Dict:
    msg_obj = await consumer.getone()

    if not msg_obj:
        return {}

    msg = msg_obj.value.decode("utf-8")
    logging.info(f"Polling: {msg}")

    return json.loads(msg)


def process_msg(msg: Dict) -> Dict:
    """
    Placeholder for processing the message.
    Currently does nothing and just returns the input.
    """
    return msg


async def check_es_health(
    es_baseurl: str, es_user: str, es_pass: str
) -> ClientResponse:
    es_url = f"{es_baseurl}/_cluster/health"

    async with ClientSession() as session:
        async with session.get(es_url, auth=BasicAuth(es_user, es_pass)) as response:
            if response.status == 200:
                health_info = await response.json()
            else:
                logging.error(
                    f"Failed to get health info: {response.status} - {await response.text()}"
                )

    return response


async def send_to_es(
    es_baseurl: str, es_user: str, es_pass: str, index_name: str, doc_id: str, msg: Dict
) -> ClientResponse:
    es_url = f"{es_baseurl}/{index_name}/_doc/{doc_id}"

    async with ClientSession() as session:
        async with session.put(
            es_url, json=msg, auth=BasicAuth(es_user, es_pass)
        ) as response:
            logging.info(f"Index: {index_name}")
            if response.status == 201:
                logging.info("Document created successfully")
            elif response.status == 200:
                logging.info("Document updated successfully")
            else:
                logging.error(
                    f"Failed to send data to Elasticsearch. Status code: {response.status}"
                )
                logging.error(await response.text())

            response.raise_for_status()

    return response
