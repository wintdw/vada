import json
import logging
import hashlib
from typing import Dict, List
from confluent_kafka import Consumer
from aiohttp import ClientSession, ClientResponse, BasicAuth


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


def consume_msg(consumer: Consumer, poll_timeout: float = 3.0) -> Dict:
    msg_obj = consumer.poll(poll_timeout)

    if msg_obj is None:
        logging.debug("No msg received")
        return {}

    msg = msg_obj.value().decode("utf-8")
    logging.debug(f"Polling: {msg}")

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
