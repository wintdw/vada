import logging
import traceback
from fastapi import APIRouter, Request, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.insert.handler.processor import get_es_processor
from etl.insert.model.vadadoc import VadaDocument

from libs.connectors.async_es import AsyncESProcessor
from libs.utils.es_field_types import (
    determine_es_field_types,
    convert_es_field_types,
    construct_es_mappings,
)


router = APIRouter()


# This function can deal with duplicate messages
# It's being used for facebook crawler, deprecated!
@router.post("/jsonl")
async def receive_jsonl(
    request: Request, skip_es_mappings: bool = False
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
    es_processor: AsyncESProcessor = get_es_processor()

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
        if not skip_es_mappings:
            field_types = determine_es_field_types(json_docs)
            json_converted_docs = convert_es_field_types(json_docs, field_types)
            mappings = construct_es_mappings(field_types)
        else:
            json_converted_docs = json_docs
            mappings = None

        # We expect all the messages received in one chunk will be in the same index
        # so we take only the first message to get the index name
        vada_doc = VadaDocument(json_lines[0])
        index_name = vada_doc.get_index_name()

        if not index_name:
            logging.error("Missing index name: %s", vada_doc.get_doc())
            raise HTTPException(status_code=400, detail="Missing index name")

        # Create index mappings if not skipped
        if not skip_es_mappings and mappings is not None:
            mappings_response = await es_processor.create_mappings(index_name, mappings)
            if mappings_response["status"] > 400:
                status_msg = "mappings failure"
                logging.error(
                    "Failed to create mappings: %s", mappings_response["detail"]
                )
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
            content={"status": status_msg, "detail": index_response["detail"]}
        )

    except ValueError as ve:
        logging.error("ValueError: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=500) from e
    finally:
        await es_processor.close()
