import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from repository.health import health_check

router = APIRouter()


@router.get("/health")
async def check_health():
    try:
        await health_check()
    except Exception as e:
        logging.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Database Unavailable")
    return JSONResponse(content={"status": "success", "detail": "Service Available"})
