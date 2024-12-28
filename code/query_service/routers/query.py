from fastapi import APIRouter, Depends, Request  # type: ignore
from typing import Dict
from fastapi.responses import JSONResponse  # type: ignore
import requests
import json

from tools import verify_jwt, logger

router = APIRouter()


@router.get("/v1/query", tags=["Query"])
async def get_query(request: Request, jwt_dict: Dict = Depends(verify_jwt)):
    json = request.json()
    body = request.body()
    logger.info(f"{json}")
    logger.info(f"{type(json)}")
    logger.info(f"{body}")
    logger.info(f"{type(body)}")
    """
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(
        "https://dev-qe.vadata.vn/query",
        data=json.dumps(payload.dict()),
        headers=headers,
    )
    return JSONResponse(content=post_response.json())
    """
    return 200

