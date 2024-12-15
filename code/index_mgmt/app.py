# pylint: disable=import-error,wrong-import-position

"""
"""

import os
import logging
import traceback
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status, Depends

import bson

from libs.security import verify_jwt
from libs.async_es import AsyncESProcessor
from libs.async_mongo import AsyncMongoProcessor


app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()

MONGO_DB = os.getenv("MONGO_DB", "vada")
MONGO_COLL = os.getenv("MONGO_COLL", "master_indices")
MONGO_URI = ""
mongo_uri_file = os.getenv("MONGO_URI_FILE", "")
if mongo_uri_file and os.path.isfile(mongo_uri_file):
    with open(mongo_uri_file, "r", encoding="utf-8") as file:
        MONGO_URI = file.read().strip()


@app.get("/health")
async def check_health():
    """Check the health of the Elasticsearch cluster."""
    es_processor = app.state.es_processor

    response = await es_processor.check_health()
    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    logging.error(await response.text())
    raise HTTPException(status_code=response.status)


@app.get("/v1/index", response_model=Dict)
async def get_index_info(index: str = "", jwt_dict: Dict = Depends(verify_jwt)):
    """
    Get information about a specific Elasticsearch index if it exists.
    """
    es_processor = app.state.es_processor
    mongo_processor = app.state.mongo_processor
    uid = jwt_dict.get("id")

    owned_indices = await mongo_processor.find_documents(
        MONGO_DB,
        MONGO_COLL,
        {
            "userID": bson.ObjectId(uid),
        },
    )

    index_names = [owned_index["name"] for owned_index in owned_indices]

    logging.debug(index_names)

    if not index:
        # Return list of index names if no index parameter is provided
        if not index_names:
            raise HTTPException(
                status_code=404, detail="No indices found for this user."
            )
        return index_names

    try:
        index_info = await es_processor.get_index(index)
        if not index_info:
            raise HTTPException(status_code=404, detail=f"Index '{index}' not found.")
        return index_info
    except HTTPException as e:
        raise e
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Unexpected error: %s\n%s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@app.on_event("startup")
async def startup():
    """
    Initialize the Elasticsearch processor on startup.
    """
    app.state.es_processor = AsyncESProcessor(
        es_baseurl=ELASTIC_URL, es_user=ELASTIC_USER, es_pass=ELASTIC_PASSWD
    )
    app.state.mongo_processor = AsyncMongoProcessor(MONGO_URI)


@app.on_event("shutdown")
async def shutdown():
    """Close the Elasticsearch session when the app shuts down."""
    es_processor = app.state.es_processor
    mongo_processor = app.state.mongo_processor

    await es_processor.close()
    await mongo_processor.close()
