from fastapi import APIRouter, Depends
from typing import Dict
from fastapi.responses import JSONResponse

from tools import verify_jwt
from models import Payload

router = APIRouter()

@router.get("/v1/query", response_model=JSONResponse, tags=["Query"])
async def get_query(payload: Payload, jwt_dict: Dict = Depends(verify_jwt)):
    headers = {
        "Content-Type": "application/json"
    }
    post_response = requests.post("https://dev-qe.vadata.vn/query", data=json.dumps(payload), headers=headers)
    return JSONResponse(content=post_response.json())
