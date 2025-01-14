import logging
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from api.models.mappings import MappingsRequest
from api.internals.mappings import MappingsProcessor
from dependencies import get_mappings_processor

router = APIRouter()


@router.post("/mappings")
async def create_mappings(
    data: MappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        response_status, response_json = await mappings_processor.copy_mappings(
            data.user_id, data.index_name, data.index_friendly_name
        )
        if response_status < 400:
            return JSONResponse(status_code=response_status, content=response_json)
        else:
            raise HTTPException(status_code=response_status, detail=response_json)
    finally:
        await mappings_processor.close()
