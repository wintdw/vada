from fastapi import APIRouter
import time
import logging

from tools import get_logger
from services import (
    tiktok_biz_get_advertiser,
    tiktok_biz_info_advertiser,
    tiktok_biz_get_report_integrated,
    tiktok_biz_get_ad,
    tiktok_biz_get_campaign,
    tiktok_biz_get_adgroup,
    insert_post_data,
)
from handlers import (
    construct_detailed_report,
    save_report,
    generate_doc_id,
    enrich_report,
    add_insert_metadata,
)

router = APIRouter()
logger = get_logger(__name__, logging.DEBUG)


@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(start_date: str, end_date: str):
    # Get all advertisers
    advertisers = await tiktok_biz_get_advertiser()
    logger.debug(advertisers)

    index_name = "a_quang_nguyen_tiktok_ad_report"
    batch_report = []
    batch_size = 5000

    for advertiser in advertisers:
        # Get advertiser info
        advertiser_info = await tiktok_biz_info_advertiser(
            [advertiser["advertiser_id"]]
        )
        logger.debug(advertiser_info)

        # Get integrated report
        reports = await tiktok_biz_get_report_integrated(
            advertiser_id=advertiser["advertiser_id"],
            start_date=start_date,
            end_date=end_date,
        )
        logger.debug(reports)

        for report in reports:
            time.sleep(3)

            # Get ad information
            ads = await tiktok_biz_get_ad(
                advertiser_id=advertiser["advertiser_id"], ad_ids=[report["ad_id"]]
            )
            logger.debug(ads)

            if not ads:
                continue

            # Get campaign information
            campaigns = await tiktok_biz_get_campaign(
                advertiser_id=advertiser["advertiser_id"],
                campaign_ids=[ads[0]["campaign_id"]],
            )
            logger.debug(campaigns)

            # Get ad group information
            adgroups = await tiktok_biz_get_adgroup(
                advertiser_id=advertiser["advertiser_id"],
                campaign_ids=[ads[0]["campaign_id"]],
                adgroup_ids=[ads[0]["adgroup_id"]],
            )
            logger.debug(adgroups)

            # Create and process report
            report_data = construct_detailed_report(
                report=report,
                advertiser_info=advertiser_info[0] if advertiser_info else {},
                campaign_info=campaigns[0] if campaigns else {},
                adgroup_info=adgroups[0] if adgroups else {},
                ad_info=ads[0] if ads else {},
            )

            if not report_data:
                continue

            logger.debug(report_data)

            doc_id = generate_doc_id(report_data)
            logger.debug(doc_id)

            enriched_report = enrich_report(report_data, doc_id, index_name)
            logger.info(enriched_report)

            batch_report.append(enriched_report)
            if len(batch_report) == batch_size:
                insert_json = await insert_post_data(
                    add_insert_metadata(batch_report, index_name)
                )
                logger.info(insert_json)
                batch_report = []

            save_report(enriched_report, "report.jsonl")

    # Insert any remaining reports
    if batch_report:
        insert_json = await insert_post_data(
            add_insert_metadata(batch_report, index_name)
        )
        logger.info(insert_json)
