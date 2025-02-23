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

router = APIRouter()


@router.post("/mappings")
async def copy_mappings(
    data: CopyMappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        response = await mappings_processor.copy_mappings(
            data.user_id, data.index_name, data.index_friendly_name
        )
        if response["status"] >= 400:
            logging.error(response["detail"])
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return JSONResponse(status_code=response["status"], content=response["detail"])
    finally:
        await mappings_processor.close()


@router.put("/mappings")
async def set_es_mappings(
    data: SetESMappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        await mappings_processor.set_es_mappings(data.index_name, data.mappings)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "detail": f"Mappings set for index: {data.index_name}",
            },
        )
    finally:
        await mappings_processor.close()


@router.put("/crm/mappings")
async def set_es_mappings(
    data: SetCRMMappingsRequest,
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    try:
        await mappings_processor.set_crm_mappings(
            data.user_id,
            data.index_name,
            data.index_friendly_name,
            data.mappings,
            data.id_field,
            data.agg_field,
            data.time_field,
        )
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "detail": f"Mappings set for index: {data.index_name}",
            },
        )
    finally:
        await mappings_processor.close()
