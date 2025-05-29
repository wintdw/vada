import logging
from typing import Dict

from fastapi import APIRouter  # type: ignore

from hander.auth import TikTokShopAuth

router = APIRouter()


@router.get("/ingest/partner/google/ad/auth")
async def get_auth():
    pass
