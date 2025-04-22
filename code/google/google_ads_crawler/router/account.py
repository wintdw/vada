import logging
from typing import Optional

from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from handler.customer import (
    get_manager_accounts,
    get_non_manager_accounts,
    get_all_accounts,
    get_child_accounts,
)
from model.google import GoogleAdsCredentials
from dependency.google import get_google_ads_client

router = APIRouter()


@router.get("/google/accounts")
async def get_customers(
    credentials: GoogleAdsCredentials,
    account_type: Optional[str] = None,
):
    """
    Get Google Ads accounts with their hierarchy structure

    Args:
        credentials: Google Ads API credentials
        account_type: Optional filter for account type ('manager', 'client', or None for all)
    """
    try:
        ga_client = await get_google_ads_client(credentials)

        if account_type == "manager":
            accounts = await get_manager_accounts(ga_client)

            # Always get child accounts for managers
            for account in accounts:
                children = await get_child_accounts(ga_client, account["customer_id"])
                account["child_accounts"] = children
                account["child_count"] = len(children)

            return JSONResponse(
                content={
                    "account_type": "manager",
                    "total_accounts": len(accounts),
                    "accounts": accounts,
                }
            )

        elif account_type == "client":
            accounts = await get_non_manager_accounts(ga_client)
            return JSONResponse(
                content={
                    "account_type": "client",
                    "total_accounts": len(accounts),
                    "accounts": accounts,
                }
            )

        else:
            # Get all accounts
            all_accounts = await get_all_accounts(ga_client)

            # Always get child accounts for manager accounts
            for account in all_accounts["manager_accounts"]:
                children = await get_child_accounts(ga_client, account["customer_id"])
                account["child_accounts"] = children
                account["child_count"] = len(children)

            return JSONResponse(
                content={
                    "account_type": "all",
                    **all_accounts,
                }
            )

    except Exception as e:
        logging.error(f"Error fetching Google Ads accounts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching Google Ads accounts: {str(e)}"
        )
