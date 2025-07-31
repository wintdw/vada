import logging
import traceback
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.insert.model.insert import InsertRequest
from etl.insert.handler.processor import get_es_processor
from etl.insert.model.vadadoc import VadaDocument

from libs.connectors.async_es import AsyncESProcessor, ESException
from libs.utils.es_field_types import (
    determine_es_field_types,
    convert_es_field_types,
    construct_es_mappings,
)


router = APIRouter()


# This function can deal with duplicate messages
@router.post("/json")
async def insert_json(request: InsertRequest) -> JSONResponse:
    """
    Main function to process JSON data received from HTTP endpoint

    Args:
        request (InsertRequest): Request body containing meta information and data

    Raises:
        HTTPException: when problems arise

    Returns:
        JSONResponse: number of consumed messages
    """
    es_processor: AsyncESProcessor = get_es_processor()

    try:
        status_msg = "success"
        index_name = request.meta.get("index_name")

        if not index_name:
            logging.error("Missing index name in meta data")
            raise HTTPException(
                status_code=400,
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
                status_code=500,
                detail=mappings_response["detail"],
            )

        index_response = await es_processor.bulk_index_docs(
            index_name, json_converted_docs
        )
        if index_response["status"] not in {200, 201}:
            status_msg = "index failure"
            logging.error("Failed to index documents: %s", index_response["detail"])
            raise HTTPException(
                status_code=500,
                detail=index_response["detail"],
            )

        return JSONResponse(
            content={
                "status": status_msg,
                "mappings": mappings,
                "detail": index_response["detail"],
            }
        )
    except ESException as es_exc:
        logging.error("Elasticsearch exception: %s", es_exc)
        raise HTTPException(
            status_code=es_exc.status_code,
            detail=es_exc.detail,
        )
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=500) from e
    finally:
        await es_processor.close()
