from fastapi import APIRouter, Depends, Request  # type: ignore
from typing import Dict
from fastapi.responses import JSONResponse  # type: ignore
import requests
import json

from tools import verify_jwt, logger

router = APIRouter()
PERMISSION_ENDPOINT = ""
QUERY_ENGINE_ENDPOINT = "https://dev-qe.vadata.vn/query"

@router.get("/v1/filter", tags=["Filter"])
async def get_query(request: Request, jwt_dict: Dict = Depends(verify_jwt)):
    headers = {"Content-Type": "application/json"}
    try:
        json = await request.json()
        logger.info(f"Received object: {json}")
        post_response = requests.post(
            QUERY_ENGINE_ENDPOINT,
            headers=headers,
            json=json
        )
        return JSONResponse(content=post_response.json())
    except Exception as err:
        logger.error(f"{err}")
