import logging
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
        response = await mappings_processor.add_user(
            data.user_name, data.user_email, data.user_passwd
        )

        msg = f"User created: {data.user_name}, email: {data.user_email}"
        logging.info(msg)

        if response["status"] >= 400:
            logging.error(response["detail"])
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return JSONResponse(status_code=response["status"], content=response["detail"])
    finally:
        await mappings_processor.close()
