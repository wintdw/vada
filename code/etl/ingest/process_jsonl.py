import asyncio
import logging
import traceback
from typing import Dict, List

# custom libs
from etl.libs.vadadoc import VadaDocument
from libs.connectors.async_kafka import AsyncKafkaProcessor
from libs.connectors.async_es import AsyncESProcessor
from libs.connectors.mappings import MappingsClient
from libs.utils.es_field_types import (
    determine_es_field_types,
    convert_es_field_types,
    construct_es_mappings,
)


# Create a global lock for setting mappings
set_mappings_lock = asyncio.Lock()


async def prepare_jsonl(json_lines: List[str], user_id: str) -> Dict:
    json_docs = []

    for line in json_lines:
        try:
            vada_doc = VadaDocument(line)
        except RuntimeError as json_err:
            logging.error("Invalid JSON format: %s - %s", line, json_err)

        vada_doc.populate_ingestor_metadata()
        vada_doc.set_user_id(user_id)
        json_docs.append(vada_doc.get_doc())

    # Take the first message to get the index name
    index_name = VadaDocument(json_docs[0]).get_index_name()
    field_types = determine_es_field_types(json_docs)
    converted_json_docs = convert_es_field_types(json_docs, field_types)
    logging.info("Field types: %s", field_types)

    return {
        "index_name": index_name,
        "field_types": field_types,
        "converted_json_docs": converted_json_docs,
    }


async def create_es_index_mappings(
    index_name: str, field_types: Dict, es_processor: AsyncESProcessor
) -> Dict:
    async with set_mappings_lock:
        mappings = construct_es_mappings(field_types)
        return await es_processor.create_mappings(index_name, mappings)


async def create_crm_mappings(
    user_id: str, index_name: str, mappings_client: MappingsClient
) -> Dict:
    async with set_mappings_lock:
        return await mappings_client.create_mappings(user_id, index_name)


async def produce_jsonl(
    app_env: str,
    index_name: str,
    json_docs: List[Dict],
    kafka_processor: AsyncKafkaProcessor,
) -> Dict:
    success = 0
    failure = 0
    failed_lines = []

    try:
        # Start the producer
        await kafka_processor.create_producer()

        kafka_topic = f"{app_env}.{index_name}"

        # to balance the partitions
        # we have by default 12 partitions each topic
        partition_cnt = 12
        batch_size = 1
        if len(json_docs) >= partition_cnt:
            batch_size = len(json_docs) // partition_cnt

        for i in range(0, len(json_docs), batch_size):
            batch = json_docs[i : i + batch_size]
            try:
                await kafka_processor.produce_messages(kafka_topic, batch, batch_size)
                success += len(batch)
            except Exception as e:
                logging.error("Failed to produce batch: %s", e)
                failure += len(batch)
                failed_lines.extend(batch)

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Unexpected error: %s\n%s", e, error_trace)
        raise e
    finally:
        await kafka_processor.close()

    return {"success": success, "failure": failure, "failed_lines": failed_lines}


async def process_jsonl(
    app_env: str,
    jsonlines: List[str],
    user_id: str,
    kafka_processor: AsyncKafkaProcessor,
    es_processor: AsyncESProcessor,
    mappings_client: MappingsClient,
):
    # This outputs the index_name, field_types and converted_json_docs
    prepare_dict = await prepare_jsonl(jsonlines, user_id)
    index_name = prepare_dict["index_name"]
    field_types = prepare_dict["field_types"]
    converted_json_docs = prepare_dict["converted_json_docs"]

    # This take the field_types to create mappings in ES
    mappings_es_dict = await create_es_index_mappings(
        index_name, field_types, es_processor
    )
    # Create mappings in CRM
    mappings_crm_dict = await create_crm_mappings(user_id, index_name, mappings_client)
    # This take the converted_json_docs to produce messages to Kafka
    produce_result_dict = await produce_jsonl(
        app_env, index_name, converted_json_docs, kafka_processor
    )

    # Accouting purpose
    if produce_result_dict["failure"] > 0:
        upload_status = "partial"
    else:
        upload_status = "success"

    # Response
    response = {
        "index": prepare_dict["index_name"],
        "status": upload_status,
        "details": f"{produce_result_dict["success"]} messages received, {produce_result_dict["failure"]} failed",
        "failures": produce_result_dict["failed_lines"],
    }

    return response
