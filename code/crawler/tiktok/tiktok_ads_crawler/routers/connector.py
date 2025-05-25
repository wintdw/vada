from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/tiktok/ad/callback", tags=["Connector"])
async def ingest_partner_tiktok_ad_callback(auth_code: str, state: str):
    from repositories import insert_crawl_info
    from models import CrawlInfo
    from services import (
        tiktok_biz_get_access_token,
        tiktok_biz_get_user_info,
        create_crm_mappings
    )

    try:
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        user_info = await tiktok_biz_get_user_info(access_token=access_token.get("access_token"))
        logger.info(user_info)
        
        crawl_info = await insert_crawl_info(CrawlInfo(
            account_id=user_info["core_user_id"],
            account_email=user_info["email"],
            vada_uid=state,
            access_token=access_token.get("access_token"),
            index_name=f"data_tiktokad_default_{state}",
            crawl_type="tiktok_business_ads"
        ))
        logger.info(crawl_info)

        mappings_response = await create_crm_mappings(
            index_name=crawl_info.index_name,
            vada_uid=state,
            account_email=user_info["email"],
        )
        logger.info(mappings_response)

        encoded_friendly_name = urlencode({"friendly_index_name": f"Tiktok Ads {user_info['email']}"})
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return RedirectResponse(url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={user_info["core_user_id"]}&account_email={user_info["email"]}&index_name={crawl_info.index_name}&{encoded_friendly_name}")

@router.get("/ingest/partner/tiktok/ad/auth", tags=["Connector"])
async def ingest_partner_tiktok_ad_auth(vada_uid: str):
    return RedirectResponse(url=f"https://business-api.tiktok.com/portal/auth?app_id=7480814660439146497&state={vada_uid}&redirect_uri=https%3A%2F%2Fapi-dev.vadata.vn%2Fingest%2Fpartner%2Ftiktok%2Fad%2Fcallback")

@router.get("/ingest/partner/facebook/ad/auth", tags=["Connector"])
async def ingest_partner_facebook_ad_auth(vada_uid: str):
    return RedirectResponse(url=f"https://www.facebook.com/v19.0/dialog/oauth?client_id=822555046472581&redirect_uri=https%3A%2F%2Fapi-dev.vadata.vn%2Fingest%2Fpartner%2Ffacebook%2Fad%2Fcallback&state={vada_uid}&scope=email,public_profile,ads_management,business_management")

@router.get("/ingest/partner/facebook/ad/callback", tags=["Connector"])
async def ingest_partner_facebook_ad_callback(vada_uid: str, access_token: str):
    from services import (
        send_to_crawler_service,
        fetch_user_info,
        create_crm_fb_mappings
    )

    try:
        user_info = await fetch_user_info(access_token=access_token)
        logger.info(user_info)

        index_name = f"data_fbad_default_{vada_uid}"
        response = await send_to_crawler_service(
            data={
                f"{user_info.get("id")}": {
                    "token": f"{access_token}",
                    "destinations": [
                        {
                            "fb_type": "fb_ad",
                            "type": "elasticsearch",
                            "index": f"{index_name}",
                        }
                    ]
                }
            }
        )
        logger.info(response)

        encoded_friendly_name = urlencode({"friendly_index_name": f"Facebook Ads {user_info.get("name")}"})

        mappings_response = await create_crm_fb_mappings(
            index_name=index_name,
            vada_uid=user_info.get("id"),
            account_email=user_info["name"],
        )
        logger.info(mappings_response)

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return RedirectResponse(url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={user_info.get("id")}&index_name={index_name}&{encoded_friendly_name}")