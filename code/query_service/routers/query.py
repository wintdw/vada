from fastapi import APIRouter

from models import Payload

router = APIRouter()

#@router.get("/v1/query/", response_model=, tags=["Query"])
@router.get("/v1/query/", tags=["Query"])
async def get_query(payload: Payload):
    print(payload)
    return 200
