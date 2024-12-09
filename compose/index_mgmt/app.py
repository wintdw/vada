import os, sys
import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Depends, status
from typing import Dict

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
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
    with open(elastic_passwd_file, "r") as file:
        ELASTIC_PASSWD = file.read().strip()

# Global object
es_processor: AsyncESProcessor


@app.get("/health")
async def check_health():
    response = await es_processor.check_health()

    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    else:
        logging.error(await response.text())
        raise HTTPException(status_code=response.status)


@app.get("/v1/index/{index_name}", response_model=Dict)
async def get_index_info(index_name: str):
    """
    Get information about a specific Elasticsearch index if it exists.
    """
    try:
        index_info = await es_processor.get_index(index_name)
        if not index_info:
            raise HTTPException(
                status_code=404, detail=f"Index '{index_name}' not found."
            )
        return index_info
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Unexpected error: {e}\n{error_trace}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.on_event("startup")
async def startup():
    """
    Initialize the Elasticsearch processor on startup.
    """
    global es_processor
    es_processor = AsyncESProcessor(
        es_baseurl=ELASTIC_URL, es_user=ELASTIC_USER, es_pass=ELASTIC_PASSWD
    )
    await es_processor.check_health()


@app.on_event("shutdown")
async def shutdown():
    """Close the Elasticsearch session when the app shuts down."""
    await es_processor.close()
