# pylint: disable=import-error,wrong-import-position

"""
"""

import traceback
import logging
import asyncio
from typing import Dict, Optional, Tuple

import libs.utils
from libs.crm import CRMAPI
from libs.async_es import AsyncESProcessor
from libs.async_kafka import AsyncKafkaProcessor


class AsyncProcessor:
    def __init__(
        self,
        kafka_broker: str,
        es_conf_dict: Dict,
        crm_conf_dict: Dict,
    ):
        self.lock = asyncio.Lock()
        self.kafka = AsyncKafkaProcessor(kafka_broker)
        self.es = AsyncESProcessor(
            es_conf_dict["url"], es_conf_dict["user"], es_conf_dict["passwd"]
        )
        # crm_conf_dict = {"auth": {"username": "", "password": ""}, "baseurl": ""}
        self.crm = CRMAPI(crm_conf_dict["baseurl"])
        self.crm_user = crm_conf_dict["auth"]["username"]
        self.crm_passwd = crm_conf_dict["auth"]["password"]

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

        doc = libs.utils.remove_fields(msg, ["__vada"])
        doc_id = libs.utils.generate_docid(doc)
        # logging.info(doc)

        # send to ES
        response = await self.es.send_to_es(index_name, doc_id, doc)
        if response.status not in {200, 201}:
            logging.error("Failed to send to ES: %s - %s", doc, await response.text())

        return (user_id, index_name, index_friendly_name)

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self, topic: str, group_id: str = "default"):
        # init the consumer explicitly
        await self.kafka.create_consumer(topic, group_id)

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
                            index_exists = await self.crm.check_index_created(
                                index_name
                            )
                            if not index_exists:
                                await self.set_mapping(
                                    user_id, index_name, index_friendly_name
                                )
                        except Exception as e:
                            error_trace = traceback.format_exc()
                            logging.error(
                                "Exception on setting Mappings for index_name: %s\nTraceback: %s",
                                e,
                                error_trace,
                            )

        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error("Exception: %s\nTraceback: %s", e, error_trace)
            raise

    async def set_mapping(
        self, user_id: str, index_name: str, index_friendly_name: str
    ):
        es_mapping = await self.es.get_es_index_mapping(index_name)
        mappings = es_mapping[index_name]["mappings"]
        logging.info("Setting mappings: %s", mappings)

        # Auth & reauth
        if not await self.crm.is_auth():
            await self.crm.auth(self.crm_user, self.crm_passwd)

        # Set the mapping in CRM
        await self.crm.set_mappings(user_id, index_name, index_friendly_name, mappings)
