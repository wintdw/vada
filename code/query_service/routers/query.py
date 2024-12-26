from fastapi import APIRouter, Depends  # type: ignore
from typing import Dict
from fastapi.responses import JSONResponse  # type: ignore
import requests
import json

from tools import verify_jwt
from models import Payload

router = APIRouter()


@router.get("/v1/query", tags=["Query"])
async def get_query(payload: Payload, jwt_dict: Dict = Depends(verify_jwt)):
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(
        "https://dev-qe.vadata.vn/query",
        data=json.dumps(payload.dict()),
        headers=headers,
    )
    return JSONResponse(content=post_response.json())
