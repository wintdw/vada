from fastapi import APIRouter, Depends, Request  # type: ignore
from typing import Dict
from fastapi.responses import JSONResponse  # type: ignore
import requests
import json

from tools import verify_jwt, setup_logger
from models import JWTPayload

router = APIRouter()
logger = setup_logger("proxy")

PERMISSION_ENDPOINT = "https://acl.vadata.vn"
QUERY_ENGINE_ENDPOINT = "https://dev-qe.vadata.vn/query"

@router.post("/v1/proxy", tags=["Proxy"])
async def proxy(request: Request, jwt: JWTPayload = Depends(verify_jwt)):
    logger.debug(f"Authenticated as {jwt.name}")
    user_id = jwt.id
    headers = {"Content-Type": "application/json"}
    try:
        json = await request.json()
        logger.debug(f"Received object: {json}")
        index_name = json["index"]

        permission_get_response = requests.get(
            f"{PERMISSION_ENDPOINT}/v1/{user_id}/{index_name}",
        )
        permission_json = permission_get_response.json()
        logger.debug(f"Received permission response: {permission_json}")

        json["filter"] = {
            "condition": "AND",
            "rules": permission_json["data"][0]["filters"]
        }
        logger.debug(f"Sending object to QE: {json}")

        qe_post_response = requests.post(
            QUERY_ENGINE_ENDPOINT,
            headers=headers,
            json=json
        )
        logger.debug(f"Received from EQ: {qe_post_response}")
        return JSONResponse(content=qe_post_response.json())

    except Exception as err:
        logger.error(f"{err}")
