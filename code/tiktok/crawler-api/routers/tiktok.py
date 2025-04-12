from fastapi import APIRouter
import time
import json

from tools import get_logger
from services import (
  tiktok_biz_get_advertiser,
  tiktok_biz_info_advertiser,
  tiktok_biz_get_report_integrated,
  tiktok_biz_get_ad,
  tiktok_biz_get_campaign,
  tiktok_biz_get_adgroup,
)
from models import (
  AdvertiserResponse,
  ReportIntegratedResponse,
  AdResponse,
  CampaignResponse,
  AdGroupResponse
)

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(start_date: str, end_date: str):
  tiktok_response = await tiktok_biz_get_advertiser()
  logger.debug(tiktok_response)
  advertiser_response = AdvertiserResponse.model_validate(tiktok_response)
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

    time.sleep(1)
  
    tiktok_response = await tiktok_biz_info_advertiser(params={"advertiser_ids": json.dumps([advertiser.advertiser_id])})
    logger.debug(tiktok_response)

    page = 1
    report_integrated_done = False
    
    while report_integrated_done == False:
      tiktok_response = await tiktok_biz_get_report_integrated(params={
        "advertiser_id": advertiser.advertiser_id,
        "report_type": "BASIC",
        "dimensions": json.dumps(dimensions),
        "data_level": "AUCTION_AD",
        "start_date": start_date,
        "end_date": end_date,
        "metrics": json.dumps(metrics),
        "page": page,
        "page_size": 100
      })
      logger.debug(tiktok_response)
      report_integrated_response = ReportIntegratedResponse.model_validate(tiktok_response)
      logger.info(report_integrated_response)
    
      if report_integrated_response.page_info.total_page > page:
        page += 1
      else:
        report_integrated_done = True

      for report_integrated in report_integrated_response.data.list:
      
        time.sleep(1)
        
        ad_filtering = {"ad_ids": [report_integrated.dimensions.ad_id]}
        tiktok_response = await tiktok_biz_get_ad(params={
          "advertiser_id": advertiser.advertiser_id,
          "filtering": json.dumps(ad_filtering)
        })
        logger.debug(tiktok_response)
        ad_response = AdResponse.model_validate(tiktok_response)
        logger.info(ad_response)

        campaign_filtering = {"campaign_ids": [ad_response.data.list[0].campaign_id]}
        tiktok_response = await tiktok_biz_get_campaign(params={
          "advertiser_id": advertiser.advertiser_id,
          "filtering": json.dumps(campaign_filtering)
        })
        logger.debug(tiktok_response)
        campaign_response = CampaignResponse.model_validate(tiktok_response)
        logger.info(campaign_response)

        adgroup_filtering = {"campaign_ids": [ad_response.data.list[0].campaign_id], "adgroup_ids": [ad_response.data.list[0].adgroup_id]}
        tiktok_response = await tiktok_biz_get_adgroup(params={
          "advertiser_id": advertiser.advertiser_id,
          "filtering": json.dumps(adgroup_filtering)
        })
        logger.debug(tiktok_response)
        adgroup_response = AdGroupResponse.model_validate(tiktok_response)
        logger.info(adgroup_response)
