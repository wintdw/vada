import json
import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore


app = FastAPI()
logging.basicConfig(level=logging.DEBUG)


DIR_PATH = "/app/data"


@app.get("/health")
async def check_health() -> JSONResponse:
    """
    Health check function

    Returns:
        JSONResponse: Return 200 when service is available
    """
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


@app.post("/capture")
async def capture_json(request: Request):
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
        logging.error(request.body())
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    os.makedirs(DIR_PATH, exist_ok=True)

    table_fullname = json_data.get("table_fullname")
    if not table_fullname:
        raise HTTPException(
            status_code=400, detail="Missing 'table_fullname' in the request data"
        )

    date_str = datetime.now().strftime("%Y%m%d")
    file_path = os.path.join(DIR_PATH, f"{table_fullname}_{date_str}.json")

    try:
        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(json_data, file)
            file.write("\n")
        return JSONResponse(content={"detail": "Data captured successfully!"})
    except Exception as e:
        logging.error("Failed to write data to %s, %s", file_path, e)
        raise HTTPException(status_code=500)
