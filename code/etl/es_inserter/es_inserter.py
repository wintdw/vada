# pylint: disable=import-error,wrong-import-position

"""
This module is for processing jsonl and pushing to ES index
"""

import os
import json
import logging
import traceback
from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse

import libs.utils
from libs.async_es import AsyncESProcessor


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

        count = 0
        for line in json_lines:
            event = json.loads(line)

            # index_name
            index_name = (
                event.get("_vada", {})
                .get("ingest", {})
                .get("destination", {})
                .get("index", "")
            )
            if not index_name:
                if "index_name" not in event:
                    logging.error(event)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing index_name",
                    )
                index_name = event["index_name"]

            # doc_id
            doc_id = event.get("_vada", {}).get("ingest", {}).get("doc_id", "")
            if not doc_id:
                doc_id = libs.utils.generate_docid(doc)

            doc = libs.utils.remove_fields(event, ["index_name", "__meta", "_vada"])
            logging.debug(doc)

            response = await es_processor.send_to_es(index_name, doc_id, doc)
            if response.status not in {200, 201}:
                logging.error(event)
                logging.error(await response.text())
                raise HTTPException(status_code=response.status)

            count += 1

        return JSONResponse(
            content={
                "status": "success",
                "detail": f"{count} messages successfully written",
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error("Exception: %s\nTraceback: %s", e, error_trace)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    finally:
        await es_processor.close()
