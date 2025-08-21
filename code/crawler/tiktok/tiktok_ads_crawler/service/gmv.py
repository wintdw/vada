import json
import logging
from typing import Dict, List

from tool.requests import get
from model.setting import settings


async def tiktok_biz_get_gmv_max_campaign_detail(
    access_token: str, advertiser_id: str, campaign_id: str
) -> Dict:
    """
    Get the details of a GMV Max Campaign.
    """
    url = f"{settings.TIKTOK_BIZ_API_URL}/campaign/gmv_max/info/"
    params = {
        "advertiser_id": advertiser_id,
        "campaign_id": campaign_id,
    }

    request_json = await get(
        url=url,
        access_token=access_token,
        params=params,
    )

    if request_json.get("code") == 0 and "data" in request_json:
        return request_json["data"]

    logging.error(f"Failed to retrieve GMV Max Campaign details: {request_json}")
    return {}


async def get_gmv_max_campaigns(
    access_token: str,
    advertiser_id: str,
    date_start: str,
    date_end: str,
) -> List[Dict]:
    """
    Retrieve GMV Max Campaigns within an ad account.
    date_start and date_end are in YYYY-MM-DD (UTC), will be used directly for API.
    """
    url = f"{settings.TIKTOK_BIZ_API_URL}/gmv_max/campaign/get/"
    all_campaigns = []
    total_number = 0
    total_page = 1
    page = 1

    # Use date_start and date_end directly, format as required by API
    start_time = f"{date_start} 00:00:00"
    end_time = f"{date_end} 23:59:59"

    filtering = {
        "gmv_max_promotion_types": ["PRODUCT_GMV_MAX", "LIVE_GMV_MAX"],
        "creation_filter_start_time": start_time,
        "creation_filter_end_time": end_time,
    }

    while True:
        params = {
            "advertiser_id": advertiser_id,
            "filtering": json.dumps(filtering),
            "page": page,
            "page_size": 100,
        }

        request_json = await get(
            url=url,
            access_token=access_token,
            params=params,
        )

        if request_json.get("code") != 0 or "data" not in request_json:
            logging.error(
                f"[{advertiser_id}] Failed to retrieve GMV Max Campaigns: {request_json}"
            )
            return all_campaigns

        data = request_json["data"]
        campaigns = data.get("list", [])
        all_campaigns.extend(campaigns)

        page_info = data.get("page_info", {})
        total_number = page_info.get("total_number", len(all_campaigns))
        total_page = page_info.get("total_page", page)

        if page >= total_page:
            break
        page += 1

    if len(all_campaigns) != total_number:
        logging.warning(
            f"[{advertiser_id}] Total campaigns fetched ({len(all_campaigns)}) does not match expected total ({total_number})"
        )
    return all_campaigns
