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
    response = await mappings_processor.es.check_health()
    if response.status < 400:
        return JSONResponse(content={"status": "ok", "detail": "Service Available"})
    else:
        logging.error(await response.text())
        raise HTTPException(status_code=response.status, detail="Service Unavailable")
