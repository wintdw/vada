# pylint: disable=import-error,wrong-import-position

import logging
import asyncio
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

# custom libs
from etl.libs.insert_client import InsertClient
from etl.ingest.model.ingest import IngestRequest
from etl.ingest.model.setting import settings

from libs.connectors.mappings import MappingsClient


app = FastAPI()
# asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
set_mappings_lock = asyncio.Lock()


@app.get("/health")
async def check_health():
    """Check the health of Mappings service."""
    mappings_client = MappingsClient(settings.MAPPINGS_BASEURL)
    mappings_response = await mappings_client.check_health()

    if mappings_response["status"] < 400:
        return JSONResponse(content={"status": "available"})
    else:
        logging.error(mappings_response["detail"])

    raise HTTPException(
        status_code=mappings_response["status"],
        detail=mappings_response["detail"],
    )


@app.post("/v1/json")
async def handle_json(request: IngestRequest):
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
    user_id = request.meta.get("user_id")
    index_name = request.meta.get("index_name")
    index_friendly_name = request.meta.get("index_friendly_name", None)
    documents = request.data

    async with InsertClient(settings.INSERT_BASEURL) as insert_client:
        # Example usage
        insert_response = await insert_client.insert_json(index_name, documents)

    mappings_client = MappingsClient(settings.MAPPINGS_BASEURL)

    # Do once at a time
    async with set_mappings_lock:
        mappings_reponse = await mappings_client.copy_mappings(
            user_id, index_name, index_friendly_name
        )

    return JSONResponse(
        content={
            "insert": insert_response,
            "mappings": mappings_reponse,
        }
    )
