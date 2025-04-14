import logging
import traceback
from typing import Dict, List

# custom libs
from .mappings import create_es_mappings, create_crm_mappings
from etl.libs.vadadoc import VadaDocument
from libs.connectors.async_kafka import AsyncKafkaProcessor
from libs.connectors.mappings import MappingsClient

from libs.utils.es_field_types import determine_es_field_types, convert_es_field_types


async def prepare(
    data: List[Dict],
    user_id: str,
    index_name: str,
    index_friendly_name: str = None,
) -> Dict:
    processed_docs = []

    for doc in data:
        try:
            vada_doc = VadaDocument(doc)
            vada_doc.populate_ingestor_metadata(
                user_id, index_name, index_friendly_name
            )
            processed_docs.append(vada_doc.get_doc())
        except RuntimeError as err:
            logging.error("Invalid document format: %s - %s", doc, err)

    if not processed_docs:
        raise RuntimeError("No valid documents to process")

    # Take the first message to get the index name
    # if index_name is None:
    #     index_name = VadaDocument(processed_docs[0]).get_index_name()
    field_types = determine_es_field_types(processed_docs)
    converted_json_docs = convert_es_field_types(processed_docs, field_types)
    logging.info("Field types: %s", field_types)

    return {
        "user_id": user_id,
        "index_name": index_name,
        "index_friendly_name": index_friendly_name,
        "field_types": field_types,
        "data": converted_json_docs,
    }


async def produce(
    kafka_processor: AsyncKafkaProcessor,
    app_env: str,
    index_name: str,
    data: List[Dict],
) -> Dict:
    """Produce messages to Kafka in batches.

    Args:
        kafka_processor: AsyncKafkaProcessor instance for Kafka operations
        app_env: Environment name (e.g., 'dev', 'prod')
        index_name: Name of the index to be used in topic name
        data: List of dictionaries containing the data to be sent to Kafka

    Returns:
        Dict containing:
            - success (int): Number of successfully processed messages
            - failure (int): Number of failed messages
            - failures (List[Dict]): List of failed items with their error reasons
                - data: The original data that failed
                - error: The error message explaining why it failed
                - timestamp: When the error occurred

    Raises:
        Exception: If there's an unexpected error during processing
    """
    success = 0
    failure = 0
    failures = []

    try:
        # Start the producer
        await kafka_processor.create_producer()

        kafka_topic = f"{app_env}.{index_name}"

        # to balance the partitions
        # we have by default 12 partitions each topic
        partition_cnt = 12
        batch_size = 1
        if len(data) >= partition_cnt:
            batch_size = len(data) // partition_cnt

        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            try:
                await kafka_processor.produce_messages(kafka_topic, batch, batch_size)
                success += len(batch)
            except Exception as e:
                error_msg = str(e)
                logging.error("Failed to produce batch: %s", error_msg)
                failure += len(batch)
                # Add failed items with error details
                failures.extend([{"data": item, "error": error_msg} for item in batch])

    except Exception as e:
        error_trace = traceback.format_exc()
        error_msg = f"{str(e)}\n{error_trace}"
        logging.error("Unexpected error: %s", error_msg)
        # Add remaining items as failures
        failures.extend([{"data": item, "error": error_msg} for item in data[success:]])
        failure += len(data[success:])
        raise e
    finally:
        await kafka_processor.close()

    return {"success": success, "failure": failure, "failures": failures}


async def process(
    kafka_processor: AsyncKafkaProcessor,
    mappings_client: MappingsClient,
    data: List[Dict],
    app_env: str,
    user_id: str,
    index_name: str,
    index_friendly_name: str = None,
) -> Dict:
    """Process data through the ETL pipeline.

    Args:
        kafka_processor: AsyncKafkaProcessor instance for Kafka operations
        mappings_client: MappingsClient instance for mapping operations
        app_env: Environment name (e.g., 'dev', 'prod')
        data: List of dictionaries containing the data to be processed
        user_id: ID of the user making the request
        index_name: Name of the index to be created/used
        index_friendly_name: Optional friendly name for the index

    Returns:
        Dict containing:
            - index: Name of the index
            - status: 'success' or 'partial'
            - details: Summary of processing results
            - failures: List of failed items with error details
    """
    # Prepare and validate documents
    prepare_dict = await prepare(data, user_id, index_name, index_friendly_name)

    # Create ES mappings
    mappings_es_dict = await create_es_mappings(
        mappings_client, prepare_dict["index_name"], prepare_dict["field_types"]
    )

    # Create CRM mappings
    mappings_crm_dict = await create_crm_mappings(
        mappings_client,
        prepare_dict["user_id"],
        prepare_dict["index_name"],
        prepare_dict["index_friendly_name"],
    )

    # Produce messages to Kafka
    produce_result_dict = await produce(
        kafka_processor, app_env, prepare_dict["index_name"], prepare_dict["data"]
    )

    # Determine upload status
    upload_status = "success" if produce_result_dict["failure"] == 0 else "partial"

    # Prepare response
    response = {
        "index": prepare_dict["index_name"],
        "status": upload_status,
        "details": f"{produce_result_dict['success']} msgs received, {produce_result_dict['failure']} failed",
        "failures": produce_result_dict["failures"],
    }

    return response
