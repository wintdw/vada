# pylint: disable=import-error,wrong-import-position

"""
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple
from aiohttp import ClientResponseError  # type: ignore

import etl.libs.utils
from etl.libs.mappings import MappingsClient
from libs.connectors.async_es import AsyncESProcessor
from libs.connectors.async_kafka import AsyncKafkaProcessor


class AsyncProcessor:
    def __init__(self, kafka_broker: str, es_conf_dict: Dict, mappings_url: str):
        self.lock = asyncio.Lock()
        self.mappings = MappingsClient(mappings_url)
        self.kafka = AsyncKafkaProcessor(kafka_broker)
        self.es = AsyncESProcessor(
            es_conf_dict["url"], es_conf_dict["user"], es_conf_dict["passwd"]
        )

    async def process_msg(self, msg: Dict) -> Optional[Tuple[str, str, str]]:
        """
        Function to process single message from Kafka and send to ES.

        Returns
        (user_id, index_name, index_friendly_name) on success, None otherwise.
        """
        meta = msg.get("__vada", {})
        index_name = meta.get("index_name")
        index_friendly_name = meta.get("index_friendly_name", index_name)
        user_id = meta.get("user_id")

        # Skip if essential data is missing
        if not index_name or not user_id:
            logging.warning("Missing required fields, skipping message: %s", msg)
            return None

        doc = etl.libs.utils.remove_fields(msg, ["__vada"])
        doc_id = etl.libs.utils.generate_docid(doc)
        # logging.info(doc)

        # send to ES
        response = await self.es.send_to_es(index_name, doc_id, doc)
        if response.status not in {200, 201}:
            logging.error("Failed to send to ES: %s - %s", doc, await response.text())

        return (user_id, index_name, index_friendly_name)

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self, topic_pattern: str, group_id: str = "default"):
        # init the consumer explicitly
        await self.kafka.create_consumer(topic_pattern, group_id)

        try:
            while True:
                input_msgs = await self.kafka.consume_messages()
                # If no message retrieved
                if not input_msgs:
                    await asyncio.sleep(3.0)
                    continue

                # Use set to avoid duplicate mappings
                unique_tuples = set()
                for input_msg in input_msgs:
                    user_id, index_name, index_friendly_name = await self.process_msg(
                        input_msg
                    )
                    unique_tuples.add((user_id, index_name, index_friendly_name))

                for user_id, index_name, index_friendly_name in unique_tuples:
                    # Do not run concurrently
                    async with self.lock:
                        try:
                            response_json = await self.mappings.create_mappings(
                                user_id, index_name, index_friendly_name
                            )
                            logging.info(
                                "Mappings created for user: %s, index: %s, response: %s",
                                user_id,
                                index_name,
                                response_json,
                            )
                        # it will raise httpexpetion on failure, but we do not stop the process
                        except ClientResponseError as e:
                            logging.warning(f"Error creating Mappings: {e}")

        except Exception as e:
            logging.error(f"Error creating Mappings: {e}", exc_info=True)
            raise
