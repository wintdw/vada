import logging
from fastapi import APIRouter, HTTPException, Depends, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from api.models.mappings import MappingsRequest
from api.internals.mappings import MappingsProcessor
from dependencies import get_mappings_processor

router = APIRouter()


@router.post("/mappings")
async def create_mapping(
    data: MappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        await mappings_processor.copy_mapping(data.user_id, data.index_name)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Mapping created successfully"},
        )
    except Exception as e:
        logging.error(f"Error creating mapping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
