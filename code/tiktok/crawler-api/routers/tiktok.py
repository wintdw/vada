from fastapi import APIRouter, HTTPException

from tools import get_logger

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/v1/tiktok", tags=["Tiktok"])
async def get_group(start_date: str = None, end_date: str = None):
    if start_date and end_date:
        return {"start_date": start_date, "end_date": end_date}
    elif start_date:
        return {"message": f"Filtering from {start_date} onwards"}
    elif end_date:
        return {"message": f"Filtering up to {end_date}"}
    return {"message": "No date range provided"}
