import logging
from typing import Dict, List

from tool.requests import post, get
from model.setting import settings


async def tiktok_biz_get_access_token(auth_code: str) -> Dict:
    """
    Fetch access token using authorization code.

    Args:
        auth_code (str): The authorization code

    Returns:
        Dict: A dictionary containing the access token and other information
    """
    payload = {
        "app_id": settings.TIKTOK_BIZ_APP_ID,
        "secret": settings.TIKTOK_BIZ_SECRET,
        "auth_code": auth_code,
    }
    request_json = await post(
        url=f"{settings.TIKTOK_BIZ_API_URL}/oauth2/access_token/", json=payload
    )
    if "data" in request_json and "access_token" in request_json["data"]:
        return request_json["data"]

    logging.error(f"Failed to retrieve access token: {request_json}")
    return {}


async def tiktok_biz_get_advertisers(access_token: str) -> List[Dict]:
    """
    Fetch all advertisers in the account.

    Returns:
        List[Dict]: A list of dictionaries containing advertiser information
    """
    request_json = await get(
        url=f"{settings.TIKTOK_BIZ_API_URL}/oauth2/advertiser/get/",
        access_token=access_token,
        params={
            "app_id": settings.TIKTOK_BIZ_APP_ID,
            "secret": settings.TIKTOK_BIZ_SECRET,
        },
    )

    if "data" in request_json and "list" in request_json["data"]:
        return request_json["data"]["list"]

    logging.error(f"Failed to retrieve advertiser info: {request_json}")
    return []
