import logging

from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from handler.account import get_manager_accounts
from model.ga_client import GoogleAdsCredentials
from dependency.google_ad_client import get_google_ads_client

router = APIRouter()


@router.get("/google/accounts")
async def fetch_google_accounts(credentials: GoogleAdsCredentials):
    """
    Get Google Ads accounts with their hierarchy structure

    Args:
        credentials: Google Ads API credentials
    """
    try:
        ga_client = await get_google_ads_client(credentials)

        accounts = await get_manager_accounts(ga_client)

        return JSONResponse(
            content={"total_mcc_accounts": len(accounts), "hierachy": accounts}
        )

    except Exception as e:
        logging.error(f"Error fetching Google Ads accounts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching Google Ads accounts: {str(e)}"
        )
