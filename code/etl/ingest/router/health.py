import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.ingest.model.setting import settings
from libs.connectors.mappings import MappingsClient


router = APIRouter()


@router.get("/health")
async def check_health():
    """Check the health of Mappings service."""
    mappings_client = MappingsClient(settings.MAPPINGS_BASEURL)
    mappings_response = await mappings_client.check_health()

    if mappings_response["status"] < 400:
        return JSONResponse(content={"status": "available"})
    else:
        logging.error(mappings_response["detail"])
        raise HTTPException(
            status_code=mappings_response["status"],
            detail=mappings_response["detail"],
        )
