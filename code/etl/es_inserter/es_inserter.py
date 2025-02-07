# pylint: disable=import-error,wrong-import-position

"""
This module is for processing jsonl and pushing to ES index
"""

import os
import json
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

from etl.libs.utils import ValidationError, remove_fields, generate_docid
from libs.connectors.async_es import AsyncESProcessor
from libs.utils.es_field_types import determine_and_convert_es_field_types


app = FastAPI()
asyncio.get_event_loop().set_debug(True)
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

es_processor = AsyncESProcessor(ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD)


@app.get("/health")
async def check_health():
    """Check the health of the Elasticsearch cluster."""
    response = await es_processor.check_health()
    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    logging.error(await response.text())
    raise HTTPException(status_code=response.status)


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
        success = 0
        failure = 0
        err_msgs = []

        json_msgs = []
        for line in json_lines:
            try:
                json_msg = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON format: {e}")
            json_msgs.append(json_msg)

        # convert
        json_converted_msgs = determine_and_convert_es_field_types(json_msgs)
        for event in json_converted_msgs:
            try:
                index_name = (
                    event.get("_vada", {})
                    .get("ingest", {})
                    .get("destination", {})
                    .get("index", "")
                )
            except Exception:
                index_name = ""

            if not index_name:
                if "index_name" not in event:
                    logging.error(event)
                    failure += 1
                    err_msgs.append("Missing index_name")
                    continue
                index_name = event["index_name"]

            doc = remove_fields(event, ["index_name", "_vada"])
            try:
                doc_id = event.get("_vada", {}).get("ingest", {}).get("doc_id", "")
            except Exception:
                doc_id = ""

            if not doc_id:
                doc_id = generate_docid(doc)
            # logging.debug(doc)

            response = await es_processor.send_to_es(index_name, doc_id, doc)
            if response.status not in {200, 201}:
                err_msg = await response.text()
                logging.error(event)
                logging.error(err_msg)
                err_msgs.append(err_msg)
                failure += 1

            success += 1

        if failure > 0:
            status_msg = "partial success"
        if success == 0:
            status_msg = "failure"

        return JSONResponse(
            content={
                "status": status_msg,
                "detail": f"{success} success, {failure} failure",
                "errors": err_msgs,
            }
        )

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    # finally:
    #     await es_processor.close()
