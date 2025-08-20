import json
import logging
from typing import List, Dict

from tool.requests import get
from model.setting import settings


async def tiktok_biz_get_user_info(access_token: str) -> Dict:
    url = f"{settings.TIKTOK_BIZ_API_URL}/user/info/"

    request_json = await get(
        url=url,
        access_token=access_token,
    )
    if "data" in request_json:
        return request_json["data"]

    logging.error(f"Failed to retrieve user info: {request_json}")
    return {}


async def tiktok_biz_info_advertisers(
    access_token: str, advertiser_ids: List[str]
) -> List[Dict]:
    """
    Fetch detailed advertiser information.

    Args:
        advertiser_ids (List[str]): List of advertiser IDs to fetch information for

    Returns:
        List[Dict]: List of dictionaries containing advertiser information
    """
    url = f"{settings.TIKTOK_BIZ_API_URL}/advertiser/info/"
    params = {"advertiser_ids": json.dumps(advertiser_ids)}

    request_json = await get(
        url=url,
        access_token=access_token,
        params=params,
    )

    if "data" in request_json and "list" in request_json["data"]:
        return request_json["data"]["list"]

    logging.error(f"Failed to retrieve advertiser info: {request_json}")
    return []
