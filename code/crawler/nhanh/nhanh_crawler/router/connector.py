import logging

from fastapi import APIRouter, HTTPException, Request  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore

from model.settings import settings
from model.index_mappings import index_mappings_data
from handler.nhanh import get_access_token
from handler.crawl_info import set_crawl_info, update_vada_uid, get_crawl_info

router = APIRouter()


@router.get("/ingest/partner/nhanh/platform/callback", tags=["Connector"])
async def get_auth(accessCode: str):
    """
    Handle the OAuth callback from Nhanh platform.

    This endpoint receives the access_code from Nhanh OAuth flow,
    exchanges it for an access token, and stores the crawl information
    in the database for future crawling operations.

    Args:
        access_code (str): The access code received from Nhanh OAuth authorization.

    Returns:
        RedirectResponse: Redirects to the connector callback URL with
                         crawl information parameters.

    Raises:
        HTTPException: If there's an error during the OAuth flow or database operation.
    """
    access_code = accessCode
    crawl_interval = 240  # Default crawl interval in minutes

    try:
        # Get access token from Nhanh API
        access_token_response = await get_access_token(access_code=access_code)
        logging.info(f"Access token response: {access_token_response}")

        # Extract data from the response
        access_token = access_token_response["accessToken"]
        business_id = access_token_response["businessId"]
        depot_ids = access_token_response["depotIds"]
        expired_datetime = access_token_response["expiredDateTime"]

        # Generate unique index name
        index_name = f"data_nhanh_{business_id}"
        friendly_index_name = f"Nhanh - {business_id}"

        # Insert/update crawl info in database
        saved_crawl_info = await set_crawl_info(
            business_id=business_id,
            index_name=index_name,
            access_token=access_token,
            expired_datetime=expired_datetime,
            crawl_interval=crawl_interval,
            depot_ids=depot_ids,
        )
        logging.info(saved_crawl_info)

        # Prepare redirect URL with crawl information
        redirect_url = (
            f"{settings.CONNECTOR_CALLBACK_URL}"
            f"?account_id={business_id}"
            f"&account_name={business_id}"
            f"&index_name={index_name}"
            f"&friendly_index_name={friendly_index_name}"
        )

        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        logging.exception(
            f"Unexpected error in Nhanh platform callback: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error during OAuth callback processing",
        )


@router.get("/ingest/partner/nhanh/platform/auth", tags=["Connector"])
async def get_auth_url():
    oauth_vesion = "2.0"
    return RedirectResponse(
        url=f"https://nhanh.vn/oauth?version={oauth_vesion}&appId={settings.NHANH_APP_ID}&returnLink={settings.NHANH_RETURN_LINK}"
    )


@router.post("/ingest/partner/nhanh/platform/vada", tags=["Connector"])
async def update_vada_uid_router(request: Request):
    request_data = await request.json()
    logging.info(f"Received request data: {request_data}")
    business_id = request_data.get("business_id")
    vada_uid = request_data.get("vada_uid")
    if not business_id:
        raise HTTPException(
            status_code=400, detail="Business ID is required in the request data"
        )

    crawl_info = await get_crawl_info(business_id=business_id)
    crawl_id = crawl_info[0]["crawl_id"]

    # update vada_uid in the database for the crawl_id
    await update_vada_uid(crawl_id=crawl_id, vada_uid=vada_uid)
    logging.info(
        f"Updated vada_uid for business_id: {business_id} with vada_uid: {vada_uid}"
    )

    return {"status": 200, "message": "Crawl info updated successfully"}


@router.get("/ingest/partner/nhanh/platform/config")
async def expose_config():
    return {"mappings": index_mappings_data["mappings"]}
