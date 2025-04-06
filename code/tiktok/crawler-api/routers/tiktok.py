from fastapi import APIRouter, HTTPException
import json

from tools import get_logger
from models import TiktokBusinessResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(start_date: str, end_date: str, page: int, page_size: int):
  from services import (
    tiktok_biz_get_advertiser,
    tiktok_biz_info_advertiser,
    tiktok_biz_get_report_integrated,
    tiktok_biz_get_ad,
    tiktok_biz_get_campaign,
    tiktok_biz_get_adgroup,
  )

  advertiser_response = TiktokBusinessResponse.model_validate(await tiktok_biz_get_advertiser())
  logger.info(advertiser_response)

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
    advertiser_info_response = TiktokBusinessResponse.model_validate(await tiktok_biz_info_advertiser(params={"advertiser_ids": json.dumps([advertiser.advertiser_id])}))
    logger.info(advertiser_info_response)

    report_integrated_response = TiktokBusinessResponse.model_validate(await tiktok_biz_get_report_integrated(params={
      "advertiser_id": advertiser.advertiser_id,
      "start_date": start_date,
      "end_date": end_date,
      "report_type": "BASIC",
      "data_level": "AUCTION_AD",
      "dimensions": json.dumps(dimensions),
      "metrics": json.dumps(metrics),
      "page": page,
      "page_size": page_size
    }))
    logger.info(report_integrated_response)

    for report_integrated in report_integrated_response.data.list:
      ad_response = TiktokBusinessResponse.model_validate(await tiktok_biz_get_ad(params={
        "advertiser_id": advertiser.advertiser_id,
        "ad_ids": [report_integrated.dimensions.ad_id],
        "page": page,
        "page_size": page_size
      }))
      logger.info(ad_response)

      """
      for ad in ad_response.data.list:
        campaign_response = TiktokBusinessResponse.model_validate(await tiktok_biz_get_campaign(params={
          "advertiser_id": advertiser.advertiser_id,
          "campaign_ids": [ad.campaign_id],
          "page": page,
          "page_size": page_size
        }))
        logger.info(campaign_response)
      """

      for ad in ad_response.data.list:
        adgroup_response = TiktokBusinessResponse.model_validate(await tiktok_biz_get_adgroup(params={
          "advertiser_id": advertiser.advertiser_id,
          "adgroup_ids": [ad.adgroup_id],
          "page": page,
          "page_size": page_size
        }))
        logger.info(adgroup_response)
