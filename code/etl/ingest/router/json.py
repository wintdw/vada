import asyncio
import logging
from fastapi.responses import APIRouter, JSONResponse  # type: ignore

# custom libs
from etl.libs.insert_client import InsertClient
from etl.ingest.model.ingest import IngestRequest
from etl.ingest.model.setting import settings

from libs.connectors.mappings import MappingsClient


router = APIRouter()


@router.post("/v1/json")
async def handle_json(
    request: IngestRequest, set_mappings_lock: asyncio.Lock
) -> JSONResponse:
    """Accept JSON data with meta information and data array.

    Format:
    {
        "meta": {
            "user_id": str,
            "index_name": str,
            "index_friendly_name": str (optional)
        },
        "data": List[Dict]
    }
    """
    user_id = request.meta.user_id
    index_name = request.meta.index_name
    index_friendly_name = request.meta.index_friendly_name
    documents = request.data

    async with InsertClient(settings.INSERT_BASEURL) as insert_client:
        # Example usage
        insert_response = await insert_client.insert_json(index_name, documents)
        logging.info(
            f"Inserted {len(documents)} documents into index {index_name} for user {user_id}: {insert_response}"
        )

    mappings_client = MappingsClient(settings.MAPPINGS_BASEURL)

    # Do once at a time
    async with set_mappings_lock:
        mappings_reponse = await mappings_client.copy_mappings(
            user_id, index_name, index_friendly_name
        )
        logging.info(
            f"Copied mappings for index {index_name} for user {user_id}: {mappings_reponse}"
        )

    return JSONResponse(
        content={
            "insert": insert_response,
            "mappings": mappings_reponse,
        }
    )
