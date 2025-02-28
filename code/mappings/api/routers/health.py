import logging
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from mappings.api.internals.mappings import MappingsProcessor
from mappings.dependencies import get_mappings_processor


router = APIRouter()


@router.get("/health")
async def health_check(
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    """Check the health of the Elasticsearch cluster."""
    try:
        health_resp = await mappings_processor.check_health()
        es_resp = health_resp["es"]
        crm_resp = health_resp["crm"]
        if es_resp["status"] >= 400 or crm_resp["status"] >= 400:
            logging.error(es_resp["detail"])
            logging.error(crm_resp["detail"])
            raise HTTPException(status_code=500, detail="Service Degraded")
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "es": "available",
                    "crm": "available",
                },
            )
    finally:
        await mappings_processor.close()
