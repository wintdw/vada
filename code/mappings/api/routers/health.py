import logging
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from api.internals.mappings import MappingsProcessor
from dependencies import get_mappings_processor


router = APIRouter()


@router.get("/health")
async def health_check(
    mappings_processor: MappingsProcessor = Depends(get_mappings_processor),
):
    """Check the health of the Elasticsearch cluster."""
    try:
        es_resp = await mappings_processor.es.check_health()
        crm_resp = await mappings_processor.crm.check_health()
        if es_resp["status"] >= 400 or crm_resp["status"] >= 400:
            logging.error(es_resp["detail"])
            logging.error(crm_resp["detail"])
            raise HTTPException(status_code=500, detail="Service Unavailable")
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "overall": "Available",
                    "es": "Available",
                    "crm": "Available",
                },
            )
    finally:
        await mappings_processor.close()
