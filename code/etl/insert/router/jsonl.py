import logging
import traceback
from fastapi import APIRouter, Request, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.insert.handler.processor import get_es_processor
from etl.insert.model.vadadoc import VadaDocument
from libs.connectors.async_es import AsyncESProcessor


router = APIRouter()


# Deprecated: used for facebook crawler, can handle duplicate messages
# No auto determine fields
@router.post("/jsonl")
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

        # We expect all the messages received in one chunk will be in the same index
        # so we take only the first message to get the index name
        vada_doc = VadaDocument(json_lines[0])
        index_name = vada_doc.get_index_name()

        if not index_name:
            logging.error("Missing index name: %s", vada_doc.get_doc())
            raise HTTPException(status_code=400, detail="Missing index name")

        index_response = await es_processor.bulk_index_docs(index_name, json_docs)
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
