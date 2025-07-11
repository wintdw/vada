from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/nhanh/platform/callback", tags=["Connector"])
async def ingest_partner_nhanh_platform_callback(accessToken: str):
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
    from repositories.crawl_info import upsert_crawl_info
    from models import NhanhCrawlInfo
    from services.nhanh import get_access_token
    
    access_token = accessToken
    try:
        # Get access token from Nhanh API
        access_token_response = await get_access_token(access_code=access_code)
        logger.info(f"Access token response: {access_token_response}")
        
        if not access_token_response or access_token_response.get("code") != 0:
            error_message = access_token_response.get("message", "Unknown error") if access_token_response else "No response from Nhanh API"
            logger.error(f"Failed to get access token: {error_message}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get access token: {error_message}"
            )
        
        # Extract data from the response
        data = access_token_response.get("data", {})
        access_token = data.get("accessToken")
        business_id = data.get("businessId")
        depot_ids = data.get("depotIds", [])
        expired_datetime = data.get("expiredDateTime")
        
        if not access_token or not business_id:
            logger.error("Missing required data from access token response")
            raise HTTPException(
                status_code=400,
                detail="Missing required data from access token response"
            )
        
        # Generate unique index name
        index_name = f"data_nhanh_{business_id}"
        
        # Create crawl info object
        crawl_info = NhanhCrawlInfo(
            index_name=index_name,
            business_id=business_id,
            access_token=access_token,
            depot_ids=depot_ids,
            expired_datetime=expired_datetime
        )
        
        # Insert/update crawl info in database
        saved_crawl_info = await upsert_crawl_info(crawl_info)
        logger.info(f"Saved crawl info: {saved_crawl_info}")
        
        # Prepare redirect URL with crawl information
        encoded_friendly_name = urlencode({"friendly_index_name": f"Nhanh Platform - {business_id}"})
        redirect_url = (
            f"{settings.CONNECTOR_CALLBACK_URL}"
            f"?account_id={business_id}"
            f"&account_name={business_id}"
            f"&index_name={saved_crawl_info.index_name}"
            f"&{encoded_friendly_name}"
        )
        
        logger.info(f"Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in Nhanh platform callback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error during OAuth callback processing"
        )

@router.get("/ingest/partner/nhanh/platform/auth", tags=["Connector"])
async def ingest_partner_nhanh_platform_auth():
    return RedirectResponse(url=f"https://nhanh.vn/oauth?version={settings.NHANH_OAUTH_VERSION}&appId={settings.NHANH_APP_ID}&returnLink={settings.NHANH_RETURN_LINK}")

@router.get("/ingest/partner/nhanh/platform/config")
async def expose_config():
    from models.index_mappings import index_mappings_data
    return {"mappings": index_mappings_data["mappings"]}