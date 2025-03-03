import logging
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from mappings.api.models.mappings import (
    CopyMappingsRequest,
    SetESMappingsRequest,
    SetCRMMappingsRequest,
)
from mappings.api.internals.mappings import MappingsProcessor
from mappings.dependencies import get_mappings_processor
from libs.utils.common import friendlify_index_name

router = APIRouter()


@router.post("/mappings")
async def copy_mappings(
    data: CopyMappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    if not data.index_friendly_name or data.index_friendly_name == data.index_name:
        index_friendly_name = friendlify_index_name(data.index_name)
    else:
        index_friendly_name = data.index_friendly_name

    try:
        response = await mappings_processor.copy_mappings(
            data.user_id,
            data.index_name,
            index_friendly_name,
            data.id_field,
            data.agg_field,
            data.time_field,
        )

        msg = f"Mappings copied for index: {data.index_name}, user: {data.user_id}"
        logging.info(msg)

        if response["status"] >= 400:
            logging.error(response["detail"])
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return JSONResponse(status_code=response["status"], content=response["detail"])
    finally:
        await mappings_processor.close()


@router.put("/es/mappings")
async def set_es_mappings(
    data: SetESMappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        await mappings_processor.set_es_mappings(data.index_name, data.mappings)

        msg = f"ES Mappings set for index: {data.index_name}"
        logging.info(msg)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "detail": msg,
            },
        )
    finally:
        await mappings_processor.close()


@router.put("/crm/mappings")
async def set_crm_mappings(
    data: SetCRMMappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    if not data.index_friendly_name or data.index_friendly_name == data.index_name:
        index_friendly_name = friendlify_index_name(data.index_name)
    else:
        index_friendly_name = data.index_friendly_name

    try:
        await mappings_processor.set_crm_mappings(
            data.user_id,
            data.index_name,
            index_friendly_name,
            data.mappings,
            data.id_field,
            data.agg_field,
            data.time_field,
        )

        msg = f"CRM Mappings set for index: {data.index_name}, user: {data.user_id}"
        logging.info(msg)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "detail": msg,
            },
        )
    finally:
        await mappings_processor.close()
