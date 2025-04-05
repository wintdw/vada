from fastapi import APIRouter, HTTPException
import json

from tools import get_logger
from models import AdvertiserResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/v1/tiktok_biz/advertiser/get/", response_model=AdvertiserResponse, tags=["Tiktok"])
async def tiktok_biz_advertiser_get():
  from services import tiktok_biz_get_advertiser

  advertiser_response = AdvertiserResponse.model_validate(await tiktok_biz_get_advertiser())
  return advertiser_response

@router.get("/v1/tiktok_biz/advertiser/info/", tags=["Tiktok"])
async def tiktok_biz_advertiser_info():
  from services import tiktok_biz_get_advertiser, tiktok_biz_info_advertiser

  advertiser_response = AdvertiserResponse.model_validate(await tiktok_biz_get_advertiser())
  for advertiser in advertiser_response.data.list:
    return await tiktok_biz_info_advertiser(params={"advertiser_ids": json.dumps([advertiser.advertiser_id])})

@router.get("/v1/tiktok_biz/campaign/get/", tags=["Tiktok"])
async def tiktok_biz_campaign_get(page: int, page_size: int):
  from services import tiktok_biz_get_advertiser, tiktok_biz_get_campaign

  advertiser_response = AdvertiserResponse.model_validate(await tiktok_biz_get_advertiser())
  for advertiser in advertiser_response.data.list:
    return await tiktok_biz_get_campaign(params={"advertiser_id": advertiser.advertiser_id, "page": page, "page_size": page_size})

@router.get("/v1/tiktok_biz/report/integrated/get/", tags=["Tiktok"])
async def tiktok_biz_report_integrated_get(start_date: str, end_date: str, page: int, page_size: int):
  from services import tiktok_biz_get_advertiser, tiktok_biz_get_report_integrated

  advertiser_response = AdvertiserResponse.model_validate(await tiktok_biz_get_advertiser())

  dimensions = ["ad_id", "stat_time_day"]
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
  ]

  for advertiser in advertiser_response.data.list:
    return await tiktok_biz_get_report_integrated(params={
      "advertiser_id": advertiser.advertiser_id,
      "start_date": start_date,
      "end_date": end_date,
      "report_type": "BASIC",
      "data_level": "AUCTION_AD",
      "dimensions": json.dumps(dimensions),
      "metrics": json.dumps(metrics),
      "page": page,
      "page_size": page_size
    })
