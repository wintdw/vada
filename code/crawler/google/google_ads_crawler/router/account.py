import logging

from fastapi import APIRouter, HTTPException, Request  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from handler.account import get_all_account_hierarchies
from dependency.google_ad_client import get_google_ads_client

router = APIRouter()


@router.get("/google/accounts")
async def fetch_google_accounts(request: Request):
    """
    Get Google Ads accounts with their hierarchy structure

    Args:
        request: The Request object containing the refresh token
    """
    body = await request.json()
    refresh_token = body.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    try:
        ga_client = await get_google_ads_client(refresh_token)

        accounts = await get_all_account_hierarchies(ga_client)

        return JSONResponse(content={"total": len(accounts), "hierachies": accounts})

    except Exception as e:
        logging.error(f"Error fetching Google Ads accounts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching Google Ads accounts: {str(e)}"
        )
