# pylint: disable=import-error,wrong-import-position

"""
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple

from etl.libs.vadadoc import VadaDocument
from libs.connectors.async_es import AsyncESProcessor
from libs.connectors.async_kafka import AsyncKafkaProcessor


class AsyncProcessor:
    def __init__(self, kafka_broker: str, es_conf_dict: Dict):
        self.lock = asyncio.Lock()
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
        (index_name, doc) on success, None otherwise.
        """
        vada_doc = VadaDocument(doc)
        index_name = vada_doc.get_index_name()
        doc = vada_doc.get_doc()

        # Skip if essential data is missing
        if not index_name:
            logging.warning("Missing required fields, skipping message: %s", doc)
            return None

        return (index_name, doc)

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self, topic_pattern: str, group_id: str = "default"):
        # init the consumer explicitly
        await self.kafka.create_consumer(topic_pattern, group_id)

        while True:
            consumed_msgs = await self.kafka.consume_messages()
            # If no message retrieved
            if not consumed_msgs:
                await asyncio.sleep(3.0)
                continue

            index_docs = {}
            for consumed_msg in consumed_msgs:
                index_name, doc = await self.extract_metadata_from_doc(consumed_msg)
                index_docs[index_name] = index_docs.get(index_name, []) + [doc]

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
