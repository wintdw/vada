# pylint: disable=import-error,wrong-import-position

"""
This module is for processing jsonl and pushing to ES index
"""

import os
import logging
import traceback
import asyncio
from fastapi import (  # type: ignore
    FastAPI,
    Request,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse  # type: ignore

from etl.libs.vadadoc import VadaDocument
from libs.connectors.async_es import AsyncESProcessor
from libs.utils.es_field_types import (
    determine_es_field_types,
    convert_es_field_types,
    construct_es_mappings,
)


app = FastAPI()
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = os.getenv("ELASTIC_PASSWD", "")
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()

es_processor = AsyncESProcessor(ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD)


@app.get("/health")
async def check_health():
    """Check the health of the Elasticsearch cluster."""
    response = await es_processor.check_health()
    if response["status"] < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    logging.error(response["detail"])
    raise HTTPException(status_code=response["status"])


# This function can deal with duplicate messages
@app.post("/jsonl")
async def receive_jsonl(request: Request) -> JSONResponse:
    """
    Main function to process jsonl received from HTTP endpoint

    Args:
        request (Request): the request

    Raises:
        HTTPException: when problems arise

    Returns:
        JSONResponse: number of consumed messages
    """
    try:
        body = await request.body()
        json_lines = body.decode("utf-8").splitlines()

        status_msg = "success"

        json_docs = []
        for line in json_lines:
            try:
                vada_doc = VadaDocument(line)
            except Exception as e:
                raise RuntimeError("Invalid JSON format: %s - %s", e, line)
            json_docs.append(vada_doc.get_doc())

        # convert
        field_types = determine_es_field_types(json_docs)
        json_converted_docs = convert_es_field_types(json_docs, field_types)
        mappings = construct_es_mappings(field_types)

        logging.info("Field types: %s", field_types)
        # We expect all the messages received in one chunk will be in the same index
        # so we take only the first message to get the index name
        index_name = vada_doc.get_index_name()

        if not index_name:
            logging.error("Missing index name: %s", vada_doc.get_doc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing index name"
            )

        # Create index mappings if not exist
        mappings_response = await es_processor.create_mappings(index_name, mappings)
        if mappings_response["status"] > 400:
            status_msg = "mappings failure"
            logging.error("Failed to create mappings: %s", mappings_response["detail"])
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=mappings_response["detail"],
            )

        index_response = await es_processor.bulk_index_docs(
            index_name, json_converted_docs
        )
        if index_response["status"] not in {200, 201}:
            status_msg = "index failure"
            logging.error("Failed to index documents: %s", index_response["detail"])
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=index_response["detail"],
            )

        return JSONResponse(
            content={"status": status_msg, "detail": index_response["detail"]}
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
