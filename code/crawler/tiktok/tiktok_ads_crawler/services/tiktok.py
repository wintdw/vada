from typing import List, Dict, Optional
import json
from tools import get, post
from tools.settings import settings

async def tiktok_biz_get_user_info(access_token: str) -> List[Dict]:    
    request_json = await get(
        url=f"{settings.TIKTOK_BIZ_API_URL}/user/info/",
        access_token=access_token,
    )
    if "data" in request_json and "id" in request_json["data"]:
        return request_json["data"]["id"]
    return []

async def tiktok_biz_get_advertiser(access_token: str) -> List[Dict]:
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
    return []


async def tiktok_biz_info_advertiser(access_token: str, advertiser_ids: List[str]) -> List[Dict]:
    """
    Fetch detailed advertiser information.

    Args:
        advertiser_ids (List[str]): List of advertiser IDs to fetch information for

    Returns:
        List[Dict]: List of dictionaries containing advertiser information
    """
    params = {"advertiser_ids": json.dumps(advertiser_ids)}
    request_json = await get(
        url=f"{settings.TIKTOK_BIZ_API_URL}/advertiser/info/",
        access_token=access_token,
        params=params,
    )

    if "data" in request_json and "list" in request_json["data"]:
        return request_json["data"]["list"]
    return []


async def tiktok_biz_get_campaign(
    access_token: str, advertiser_id: str, campaign_ids: Optional[List[str]] = None
) -> List[Dict]:
    """
    Fetch all campaign information with pagination.

    Args:
        advertiser_id (str): The ID of the advertiser
        campaign_ids (List[str], optional): List of campaign IDs to filter

    Returns:
        List[Dict]: List of campaign information dictionaries
    """
    all_campaigns: List[Dict] = []
    page: int = 1

    while True:
        params = {"advertiser_id": advertiser_id, "page": str(page), "page_size": "100"}

        if campaign_ids:
            params["filtering"] = json.dumps({"campaign_ids": campaign_ids})

        request_json = await get(
            url=f"{settings.TIKTOK_BIZ_API_URL}/campaign/get/",
            access_token=access_token,
            params=params,
        )

        if "data" in request_json and "list" in request_json["data"]:
            all_campaigns.extend(request_json["data"]["list"])
            page_info = request_json["data"].get("page_info", {})
            total_pages = page_info.get("total_page", 0)
            if page >= total_pages:
                break
            page += 1
        else:
            break

    return all_campaigns


async def tiktok_biz_get_report_integrated(
    access_token: str,
    advertiser_id: str,
    start_date: str,
    end_date: str,
    metrics: Optional[List[str]] = None,
    dimensions: Optional[List[str]] = None,
    report_type: str = "BASIC",
    data_level: str = "AUCTION_AD",
    enable_total_metrics: bool = True,
) -> List[Dict]:
    """
    Fetch integrated advertising reports with pagination.

    Args:
        advertiser_id (str): The ID of the advertiser
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
        metrics (List[str], optional): List of metrics to include
        dimensions (List[str], optional): List of dimensions to group by
        report_type (str, optional): Type of report. Defaults to 'BASIC'
        data_level (str, optional): Level of data aggregation. Defaults to 'AUCTION_AD'
        enable_total_metrics (bool, optional): Include total metrics. Defaults to True

    Returns:
        List[Dict]: List of flattened report entries
    """
    all_reports: List[Dict] = []
    page: int = 1

    if dimensions is None:
        dimensions = ["ad_id", "stat_time_day"]

    if metrics is None:
        metrics = [
            "spend",
            "billed_cost",
            "cash_spend",
            "voucher_spend",
            "cpc",
            "cpm",
            "impressions",
            "gross_impressions",
            "clicks",
            "ctr",
            "reach",
            "cost_per_1000_reached",
            "frequency",
            "conversion",
            "cost_per_conversion",
            "conversion_rate",
            "conversion_rate_v2",
            "real_time_conversion",
            "real_time_cost_per_conversion",
            "real_time_conversion_rate",
            "real_time_conversion_rate_v2",
            "result",
            "cost_per_result",
            "result_rate",
            "real_time_result",
            "real_time_cost_per_result",
            "real_time_result_rate",
            "secondary_goal_result",
            "cost_per_secondary_goal_result",
            "secondary_goal_result_rate",
            "vta_conversion",
            "cost_per_vta_conversion",
            "vta_purchase",
            "cost_per_vta_purchase",
            "vta_complete_payment",
            "cost_per_vta_payments_completed",
            "vta_complete_payment_value",
            "vta_complete_payment_roas",
            "cta_conversion",
            "cost_per_cta_conversion",
            "cta_purchase",
            "cost_per_cta_purchase",
            "engaged_view_through_conversions",
            "cost_per_engaged_view_through_conversion",
            "evta_purchase",
            "cost_per_evta_purchase",
            "evta_payments_completed",
            "cost_per_evta_payments_completed",
            "real_time_app_install",
            "real_time_app_install_cost",
            "app_install",
            "cost_per_app_install",
            "registration",
            "cost_per_registration",
            "registration_rate",
            "total_registration",
            "cost_per_total_registration",
            "purchase",
            "cost_per_purchase",
            "purchase_rate",
            "total_purchase",
            "cost_per_total_purchase",
            "value_per_total_purchase",
            "total_purchase_value",
            "total_active_pay_roas",
            "video_play_actions",
            "video_watched_2s",
            "video_watched_6s",
            "engaged_view",
            "paid_engaged_view",
            "paid_engagement_engaged_view",
            "engaged_view_15s",
            "paid_engaged_view_15s",
            "paid_engagement_engaged_view_15s",
            "average_video_play",
            "average_video_play_per_user",
            "live_views",
            "live_unique_views",
            "live_effective_views",
            "live_product_clicks"
        ]

    while True:
        params = {
            "advertiser_id": advertiser_id,
            "report_type": report_type,
            "dimensions": json.dumps(dimensions),
            "data_level": data_level,
            "start_date": start_date,
            "end_date": end_date,
            "enable_total_metrics": str(enable_total_metrics).lower(),
            "metrics": json.dumps(metrics),
            "page": str(page),
            "page_size": "100",
        }

        request_json = await get(
            url=f"{settings.TIKTOK_BIZ_API_URL}/report/integrated/get/",
            access_token=access_token,
            params=params,
        )

        if "data" in request_json and "list" in request_json["data"]:
            for report in request_json["data"]["list"]:
                flattened_report = {}
                if "dimensions" in report:
                    flattened_report.update(report["dimensions"])
                if "metrics" in report:
                    flattened_report.update(report["metrics"])
                all_reports.append(flattened_report)

            page_info = request_json["data"].get("page_info", {})
            total_pages = page_info.get("total_page", 0)
            if page >= total_pages:
                break
            page += 1
        else:
            break

    return all_reports


async def tiktok_biz_get_ad(
    access_token: str,
    advertiser_id: str,
    campaign_ids: Optional[List[str]] = None,
    adgroup_ids: Optional[List[str]] = None,
    ad_ids: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Fetch ad information with pagination.

    Args:
        advertiser_id (str): The ID of the advertiser
        campaign_ids (List[str], optional): List of campaign IDs to filter
        adgroup_ids (List[str], optional): List of ad group IDs to filter
        ad_ids (List[str], optional): List of ad IDs to filter

    Returns:
        List[Dict]: List of ad information dictionaries
    """
    all_ads: List[Dict] = []
    page: int = 1

    while True:
        params = {"advertiser_id": advertiser_id, "page": str(page), "page_size": "100"}

        filtering = {}
        if campaign_ids:
            filtering["campaign_ids"] = campaign_ids
        if adgroup_ids:
            filtering["adgroup_ids"] = adgroup_ids
        if ad_ids:
            filtering["ad_ids"] = ad_ids

        if filtering:
            params["filtering"] = json.dumps(filtering)

        request_json = await get(
            url=f"{settings.TIKTOK_BIZ_API_URL}/ad/get/",
            access_token=access_token,
            params=params,
        )

        if "data" in request_json and "list" in request_json["data"]:
            all_ads.extend(request_json["data"]["list"])
            page_info = request_json["data"].get("page_info", {})
            total_pages = page_info.get("total_page", 0)
            if page >= total_pages:
                break
            page += 1
        else:
            break

    return all_ads


async def tiktok_biz_get_adgroup(
    access_token: str,
    advertiser_id: str,
    campaign_ids: Optional[List[str]] = None,
    adgroup_ids: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Fetch ad group information with pagination.

    Args:
        advertiser_id (str): The ID of the advertiser
        campaign_ids (List[str], optional): List of campaign IDs to filter
        adgroup_ids (List[str], optional): List of ad group IDs to filter

    Returns:
        List[Dict]: List of ad group information dictionaries
    """
    all_adgroups: List[Dict] = []
    page: int = 1

    while True:
        params = {"advertiser_id": advertiser_id, "page": str(page), "page_size": "100"}

        filtering = {}
        if campaign_ids:
            filtering["campaign_ids"] = campaign_ids
        if adgroup_ids:
            filtering["adgroup_ids"] = adgroup_ids

        if filtering:
            params["filtering"] = json.dumps(filtering)

        request_json = await get(
            url=f"{settings.TIKTOK_BIZ_API_URL}/adgroup/get/",
            access_token=access_token,
            params=params,
        )

        if "data" in request_json and "list" in request_json["data"]:
            all_adgroups.extend(request_json["data"]["list"])
            page_info = request_json["data"].get("page_info", {})
            total_pages = page_info.get("total_page", 0)
            if page >= total_pages:
                break
            page += 1
        else:
            break

    return all_adgroups


async def tiktok_biz_get_access_token(
    auth_code: str
) -> Dict:
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
        url=f"{settings.TIKTOK_BIZ_API_URL}/oauth2/access_token/",
        json=payload
    )
    if "data" in request_json and "access_token" in request_json["data"]:
        return request_json["data"]
    return {}