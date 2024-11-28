import bson
import traceback
from typing import Dict

import utils
from async_es import AsyncESProcessor
from async_kafka import AsyncKafkaProcessor
from async_mongo import AsyncMongoProcessor


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

        # init the consumer explicitly
        self.kafka.create_consumer()

    # Flow: consume from kafka -> process -> send to es
    async def consume_then_produce(self, topic: str, group_id: str = "default"):
        try:
            while True:
                input_msg = await self.kafka.consume_message(topic, group_id)
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
                        f"Missing required fields, skipping message: {input_msg}"
                    )
                    continue

                doc = utils.remove_fields(input_msg, ["__meta"])
                doc_id = utils.generate_docid(doc)
                logging.info(doc)

                # send to ES
                response = await self.es.send_to_es(index_name, doc_id, doc)
                if response.status not in {200, 201}:
                    logging.error(f"Failed to send to ES: {doc}: {response.text()}")

                # copy mapping to mongo
                await self.set_mapping(
                    user_id,
                    index_name,
                    index_friendly_name,
                    mongo_db="vada",
                    mongo_coll="master_indices",
                )

        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"Exception: {e}\nTraceback: {error_trace}")
        finally:
            await self.kafka.close()
            await self.mongo.close()
            await self.es.close()

    # Set mapping if only mongo doesnt have mapping for the index
    async def set_mapping(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mongo_db: str,
        mongo_coll: str,
    ):
        mongo_mapping = await self.mongo.find_document(
            mongo_db, mongo_coll, {"name": index_name}
        )
        if mongo_mapping:
            logging.info(f"Mapping exists, do nothing: {mongo_mapping}")
            return
        else:
            es_mapping = await self.es.get_es_index_mapping(index_name)
            mapping_dict = {"name": index_name}
            mapping_dict["userID"] = bson.ObjectId(user_id)
            mapping_dict["friendly_name"] = index_friendly_name
            mapping_dict["mappings"] = es_mapping[index_name]["mappings"]
            logging.info(f"Set mapping: {mapping_dict}")
            await self.mongo.insert_document(mongo_db, mongo_coll, mapping_dict)
