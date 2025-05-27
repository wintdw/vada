import logging
from typing import Dict

from fastapi import APIRouter  # type: ignore

from handler.auth

router = APIRouter()


@router.get("/ingest/partner/google/ad/auth")
async def get_auth():