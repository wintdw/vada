from fastapi import APIRouter, HTTPException

from tools import get_logger
from models import Tiktok

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/v1/tiktok", tags=["Tiktok"])
async def tiktok_biz_get_advertiser(start_date: str = None, end_date: str = None):
  from services import tiktok_biz_get_advertiser

  return await tiktok_biz_get_advertiser()
