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
  insert_post_data
)
from models import (
  AdvertiserResponse,
  ReportIntegratedResponse,
  AdResponse,
  CampaignResponse,
  AdGroupResponse
)
from handlers import (
  create_report,
  save_report,
  generate_doc_id,
  enrich_report,
  add_insert_metadata
)

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(start_date: str, end_date: str):
  advertiser_json = await tiktok_biz_get_advertiser()
  logger.debug(advertiser_json)
  advertiser_response = AdvertiserResponse.model_validate(advertiser_json)
  logger.info(advertiser_response)

  index_name = "a_quang_nguyen_tiktok_ad_report"
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

  batch_report = []
  batch_size = 5000

  for advertiser in advertiser_response.data.list:

    time.sleep(3)
  
    advertiser_info_json = await tiktok_biz_info_advertiser(params={"advertiser_ids": json.dumps([advertiser.advertiser_id])})
    logger.debug(advertiser_info_json)

    page = 1
    report_integrated_done = False
    
    while report_integrated_done == False:
      report_integrated_json = await tiktok_biz_get_report_integrated(params={
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
      logger.debug(report_integrated_json)
      report_integrated_response = ReportIntegratedResponse.model_validate(report_integrated_json)
      logger.info(report_integrated_response)
    
      if report_integrated_response.data.page_info.total_page > page:
        page += 1
      else:
        report_integrated_done = True

      for report_integrated in report_integrated_response.data.list:
      
        time.sleep(3)
        
        ad_filtering = {"ad_ids": [report_integrated.dimensions.ad_id]}
        ad_json = await tiktok_biz_get_ad(params={
          "advertiser_id": advertiser.advertiser_id,
          "filtering": json.dumps(ad_filtering)
        })
        logger.debug(ad_json)
        ad_response = AdResponse.model_validate(ad_json)
        logger.info(ad_response)

        campaign_filtering = {"campaign_ids": [ad_response.data.list[0].campaign_id]}
        campaign_json = await tiktok_biz_get_campaign(params={
          "advertiser_id": advertiser.advertiser_id,
          "filtering": json.dumps(campaign_filtering)
        })
        logger.debug(campaign_json)
        campaign_response = CampaignResponse.model_validate(campaign_json)
        logger.info(campaign_response)

        adgroup_filtering = {"campaign_ids": [ad_response.data.list[0].campaign_id], "adgroup_ids": [ad_response.data.list[0].adgroup_id]}
        adgroup_json = await tiktok_biz_get_adgroup(params={
          "advertiser_id": advertiser.advertiser_id,
          "filtering": json.dumps(adgroup_filtering)
        })
        logger.debug(adgroup_json)
        adgroup_response = AdGroupResponse.model_validate(adgroup_json)
        logger.info(adgroup_response)

        report = create_report(
          advertiser_info=advertiser_info_json,
          report_integrated=report_integrated_json,
          ad=ad_json,
          campaign=campaign_json,
          adgroup=adgroup_json
        )
        logger.info(report)
        
        doc_id = generate_doc_id(report)
        logger.info(doc_id)

        enriched_report = enrich_report(report, doc_id, index_name)
        logger.info(enriched_report)

        batch_report.append(enriched_report)
        if len(batch_report) == batch_size:
          insert_json = await insert_post_data(add_insert_metadata(batch_report, index_name))
          logger.info(insert_json)
          batch_report = []

        save_report(enriched_report, "report.jsonl")

  if len(batch_report):
    insert_json = await insert_post_data(add_insert_metadata(batch_report, index_name))
