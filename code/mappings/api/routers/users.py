from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from mappings.api.models.users import UsersRequest
from mappings.api.internals.mappings import MappingsProcessor
from mappings.dependencies import get_mappings_processor

router = APIRouter()


@router.post("/users")
async def create_user(
    data: UsersRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        response_status, response_json = await mappings_processor.add_user(
            data.user_name, data.user_email, data.user_passwd
        )
        if response_status < 400:
            return JSONResponse(status_code=response_status, content=response_json)
        else:
            raise HTTPException(status_code=response_status, detail=response_json)
    finally:
        await mappings_processor.close()
