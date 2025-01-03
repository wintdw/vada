import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from receiver.processor import AsyncProcessor


ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()

DIR_PATH = "/app/data"

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
processor = AsyncProcessor(
    {"url": ELASTIC_URL, "user": ELASTIC_USER, "passwd": ELASTIC_PASSWD}
)


@app.get("/health")
async def check_health() -> JSONResponse:
    """
    Health check function

    Returns:
        JSONResponse: Return 200 when service is available
    """
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.post("/capture")
async def capture_json(request: Request) -> JSONResponse:
    """
    Capture JSON data from the request and save it to a file.

    Args:
        request (Request): The incoming request containing JSON data.

    Returns:
        JSONResponse: A response indicating the result of the operation.
    """
    try:
        json_data = await request.json()
    except json.JSONDecodeError:
        logging.error(await request.body())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON data"
        )

    await processor.persist_to_file(DIR_PATH, json_data)
