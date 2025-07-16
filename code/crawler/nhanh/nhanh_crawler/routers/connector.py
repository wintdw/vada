from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/nhanh/platform/callback", tags=["Connector"])
async def ingest_partner_nhanh_platform_callback(accessCode: str):
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
    
    access_code = accessCode
    try:
        # Get access token from Nhanh API
        access_token_response = await get_access_token(access_code=access_code)
        logger.info(f"Access token response: {access_token_response}")
        
        # Extract data from the response
        access_token = access_token_response.get("accessToken")
        business_id = access_token_response.get("businessId")
        depot_ids = access_token_response.get("depotIds", [])
        expired_datetime = access_token_response.get("expiredDateTime")
        
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

@router.post("/ingest/partner/nhanh/platform/vada", tags=["Connector"])
async def ingest_partner_nhanh_platform_vada(request: Request):
    from repositories.crawl_info import update_crawl_info_by_vada_uid
    
    request_data = await request.json()
    logger.info(f"Received request data: {request_data}")
    await update_crawl_info_by_vada_uid(business_id=request_data.business_id, vada_uid=request_data.vada_uid)
    return {"status": 200, "message": "Crawl info updated successfully"}

@router.get("/ingest/partner/nhanh/platform/config")
async def expose_config():
    from models.index_mappings import index_mappings_data
    return {"mappings": index_mappings_data["mappings"]}