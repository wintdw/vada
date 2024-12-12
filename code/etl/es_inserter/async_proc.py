# pylint: disable=import-error,wrong-import-position

"""
"""

import traceback
import logging
import asyncio
from typing import Dict

import bson

import libs.utils
from libs.async_es import AsyncESProcessor
from libs.async_kafka import AsyncKafkaProcessor
from libs.async_mongo import AsyncMongoProcessor


class AsyncProcessor:
    def __init__(
        self,
        kafka_broker: str,
        es_conf_dict: Dict,
        mongo_url: str,
    ):
        self.kafka = AsyncKafkaProcessor(kafka_broker)
        self.es = AsyncESProcessor(
            es_conf_dict["url"], es_conf_dict["user"], es_conf_dict["passwd"]
        )
        self.mongo = AsyncMongoProcessor(mongo_url)

        # For setting mappings
        self.lock = asyncio.Lock()

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self, topic: str, group_id: str = "default"):
        # init the consumer explicitly
        await self.kafka.create_consumer(topic, group_id)

        try:
            while True:
                input_msg = await self.kafka.consume_message()
                # If no message retrieved
                if not input_msg:
                    await asyncio.sleep(3.0)
                    continue

                # Extract __meta once to avoid redundant lookups
                meta = input_msg.get("__meta", {})
                index_name = meta.get("index_name")
                index_friendly_name = meta.get("index_friendly_name", index_name)
                user_id = meta.get("user_id")

                # Skip if essential data is missing
                if not index_name or not user_id:
                    logging.warning(
                        "Missing required fields, skipping message: %s", input_msg
                    )
                    continue

                doc = libs.utils.remove_fields(input_msg, ["__meta"])
                doc_id = libs.utils.generate_docid(doc)
                logging.info(doc)

                # send to ES
                response = await self.es.send_to_es(index_name, doc_id, doc)
                if response.status not in {200, 201}:
                    logging.error(
                        "Failed to send to ES: %s - %s", doc, await response.text()
                    )

                # copy mapping to mongo
                # run sequentially
                async with self.lock:
                    await self.set_mapping(
                        user_id,
                        index_name,
                        index_friendly_name,
                        mongo_db="vada",
                        mongo_coll="master_indices",
                    )

        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error("Exception: %s\nTraceback: %s", e, error_trace)
            raise
        finally:
            await self.kafka.close()
            await self.mongo.close()
            await self.es.close()

    # Set mapping if only mongo doesnt have mapping for the index
    # TODO: Use crm-api set mapping?
    async def set_mapping(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mongo_db: str,
        mongo_coll: str,
    ):
        filter_condition = {"name": index_name}
        mongo_mapping = await self.mongo.find_document(
            mongo_db, mongo_coll, filter_condition
        )
        if mongo_mapping:
            if "mappings" in mongo_mapping and mongo_mapping["mappings"]:
                logging.info("Mapping exists, do nothing: %s", mongo_mapping)
                return

        es_mapping = await self.es.get_es_index_mapping(index_name)
        mapping_dict = {"name": index_name}
        mapping_dict["userID"] = bson.ObjectId(user_id)
        mapping_dict["friendly_name"] = index_friendly_name
        mapping_dict["mappings"] = es_mapping[index_name]["mappings"]
        logging.info("Set mapping: %s", mapping_dict)

        await self.mongo.upsert_document(
            mongo_db, mongo_coll, filter_condition, mapping_dict
        )
