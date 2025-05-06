# pylint: disable=import-error,wrong-import-position

"""
This module is for processing jsonl and pushing to ES index
"""

import logging
import traceback
import asyncio
from fastapi import FastAPI, Request, HTTPException, status, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel  # type: ignore
from typing import List, Dict, Any

from etl.libs.vadadoc import VadaDocument
from etl.libs.processor import get_es_processor
from libs.connectors.async_es import AsyncESProcessor, ESException
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


# Create a separate thread pool for health checks
health_check_executor = ThreadPoolExecutor(max_workers=1)


# This functions is for running health check in another threadpool worker
# so it's not blocked by the main thread
def check_health_sync(es_processor: AsyncESProcessor):
    """Check the health of the Elasticsearch cluster synchronously."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(es_processor.check_health())
    finally:
        loop.run_until_complete(es_processor.close())
        loop.close()
    return response


@app.get("/health")
async def check_health(es_processor: AsyncESProcessor = Depends(get_es_processor)):
    """Check the health of the Elasticsearch cluster."""
    response = await asyncio.get_event_loop().run_in_executor(
        health_check_executor, check_health_sync, es_processor
    )

    if response["status"] >= 400:
        logging.error(response["detail"])
        raise HTTPException(status_code=response["status"])

    return JSONResponse(content={"status": "success", "detail": "Service Available"})


# This function can deal with duplicate messages
@app.post("/jsonl")
async def receive_jsonl(
    request: Request, es_processor: AsyncESProcessor = Depends(get_es_processor)
) -> JSONResponse:
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
    finally:
        await es_processor.close()


##### NEW FORMAT
class InsertRequest(BaseModel):
    meta: Dict[str, str]
    data: List[Dict[str, Any]]


# This function can deal with duplicate messages
@app.post("/json")
async def insert_json(
    request: InsertRequest, es_processor: AsyncESProcessor = Depends(get_es_processor)
) -> JSONResponse:
    """
    Main function to process JSON data received from HTTP endpoint

    Args:
        request (InsertRequest): Request body containing meta information and data
        es_processor (AsyncESProcessor): Elasticsearch processor dependency

    Raises:
        HTTPException: when problems arise

    Returns:
        JSONResponse: number of consumed messages
    """
    try:
        status_msg = "success"
        index_name = request.meta.get("index_name")

        if not index_name:
            logging.error("Missing index name in meta data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing index name in meta data",
            )

        json_docs = []
        for data in request.data:
            try:
                vada_doc = VadaDocument(data)
                json_docs.append(vada_doc.get_doc())
            except Exception as e:
                raise RuntimeError(f"Invalid JSON format: {e} - {data}")

        # convert
        field_types = determine_es_field_types(json_docs)
        json_converted_docs = convert_es_field_types(json_docs, field_types)
        mappings = construct_es_mappings(field_types)

        logging.info("Field types: %s", field_types)

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
    except ESException as es_exc:
        logging.error("Elasticsearch exception: %s", e)
        raise HTTPException(
            status_code=es_exc.status,
            detail=es_exc.detail,
        )
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    finally:
        await es_processor.close()
