# pylint: disable=import-error,wrong-import-position

"""
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple
from aiohttp import ClientResponseError  # type: ignore

from etl.libs.vadadoc import VadaDocument
from libs.connectors.mappings import MappingsClient
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

    async def extract_metadata_from_doc(
        self, doc: Dict
    ) -> Optional[Tuple[str, str, str, str]]:
        """
        Function to process single message from Kafka and send to ES.

        Returns
        (user_id, index_name, index_friendly_name, doc) on success, None otherwise.
        """
        vada_doc = VadaDocument(doc)
        index_name = vada_doc.get_index_name()
        index_friendly_name = vada_doc.get_index_friendly_name()
        user_id = vada_doc.get_user_id()
        doc = vada_doc.get_doc()

        # Skip if essential data is missing
        if not index_name or not user_id:
            logging.warning("Missing required fields, skipping message: %s", doc)
            return None

        return (user_id, index_name, index_friendly_name, doc)

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self, topic_pattern: str, group_id: str = "default"):
        # init the consumer explicitly
        await self.kafka.create_consumer(topic_pattern, group_id)

        try:
            while True:
                consumed_msgs = await self.kafka.consume_messages()
                # If no message retrieved
                if not consumed_msgs:
                    await asyncio.sleep(3.0)
                    continue

                # Use set to avoid duplicate mappings
                unique_tuples = set()
                index_docs = {}
                for consumed_msg in consumed_msgs:
                    user_id, index_name, index_friendly_name, doc = (
                        await self.extract_metadata_from_doc(consumed_msg)
                    )
                    index_docs[index_name] = index_docs.get(index_name, []) + [doc]
                    unique_tuples.add((user_id, index_name, index_friendly_name))

                # Bulk index documents to Elasticsearch
                for index_name, docs in index_docs.items():
                    try:
                        response = await self.es.bulk_index_docs(index_name, docs)
                        logging.info(
                            "Bulk indexed documents to index: %s, response: %s",
                            index_name,
                            response["detail"],
                        )
                    except Exception as e:
                        logging.error(
                            f"Error bulk indexing documents to index {index_name}: {e}",
                            exc_info=True,
                        )

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
