import asyncio
import logging
from fastapi import APIRouter  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

# custom libs
from etl.libs.insert_client import InsertClient
from etl.ingest.model.ingest import IngestRequest
from etl.ingest.model.setting import settings


router = APIRouter()
# Need to change to distributed lock for multiple instances
SET_MAPPINGS_LOCK = asyncio.Lock()


@router.post("/v1/json")
async def handle_json(request: IngestRequest) -> JSONResponse:
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

    return JSONResponse(content=insert_response)
