import logging
from fastapi import APIRouter, HTTPException, Depends, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from api.models.users import UsersRequest
from api.internals.mappings import MappingsProcessor
from dependencies import get_mappings_processor

router = APIRouter()


@router.post("/users")
async def create_users_with_mappings(
    data: UsersRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        response_status, response_json = await mappings_processor.copy_mappings(
            data.user_id, data.index_name, data.index_friendly_name
        )
        return JSONResponse(status_code=response_status, content=response_json)
    except Exception as e:
        logging.error(f"Error creating User: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
    finally:
        await mappings_processor.close()
