from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from tools.logger import get_logger
from repositories.health import health_check

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def check_health():
    try:
        await health_check()
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Database Unavailable")
    return JSONResponse(content={"status": "success", "detail": "Service Available"})
