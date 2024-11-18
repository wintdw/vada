import json
import logging
import hashlib
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorClient


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


#### MONGO
async def insert_mongo_mapping(
    mongo_uri: str, db: str, collection: str, mapping_dict: dict
):
    client = AsyncIOMotorClient(mongo_uri)

    try:
        result = await client[db][collection].insert_one(mapping_dict)
        logging.info(f"Mapping inserted successfully with _id: {result.inserted_id}")
    except Exception as e:
        logging.error(f"Error inserting mapping into MongoDB: {str(e)}")
        logging.error("Traceback: ", exc_info=True)
    finally:
        client.close()

    return result
