from fastapi import APIRouter, Depends
from typing import Dict

from tools import verify_jwt
from models import Payload

router = APIRouter()

#@router.get("/v1/query/", response_model=, tags=["Query"])
@router.get("/v1/query", tags=["Query"])
async def get_query(payload: Payload, jwt_dict: Dict = Depends(verify_jwt)):
    print(payload)
    return 200
