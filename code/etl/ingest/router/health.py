import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from etl.ingest.model.setting import settings


router = APIRouter()


@router.get("/health")
async def check_health():
    return JSONResponse(content={"status": "available"})
