from fastapi import APIRouter  # type: ignore
import logging
import time

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
logger = get_logger(__name__, logging.INFO)


@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(start_date: str, end_date: str):
    start_time = time.time()

    # Get all advertisers
    advertisers = await tiktok_biz_get_advertiser()
    logger.debug(advertisers)

    index_name = "a_quang_nguyen_tiktok_ad_report"
    batch_report = []
    batch_size = 1000
    all_enriched_reports = []

    for advertiser in advertisers:
        logger.info(f"Processing advertiser ID: {advertiser['advertiser_id']}")

        # Get advertiser info
        advertiser_info = await tiktok_biz_info_advertiser(
            [advertiser["advertiser_id"]]
        )
        logger.info(f"  → Advertiser name: {advertiser_info[0].get('name', 'N/A')}")
        logger.debug(advertiser_info)

        # Get integrated report
        reports = await tiktok_biz_get_report_integrated(
            advertiser_id=advertiser["advertiser_id"],
            start_date=start_date,
            end_date=end_date,
        )
        logger.debug(reports)

        for report in reports:
            logger.info(f"Processing report for ad_id: {report.get('ad_id')}")
            logger.info(f"  → Report date: {report.get('stat_time_day')}")
            logger.info(f"  → Report spend: {report.get('spend', '0')}")

            if float(report.get("spend", "0")) == 0:
                logger.info("    ✗ Skipping report with zero spend")
                continue

            # Get ad information
            logger.info(f"  → Getting ad information for ID: {report['ad_id']}")
            ads = await tiktok_biz_get_ad(
                advertiser_id=advertiser["advertiser_id"], ad_ids=[report["ad_id"]]
            )

            # Get campaign information
            logger.info(
                f"  → Getting campaign information for ID: {ads[0]['campaign_id']}"
            )
            campaigns = await tiktok_biz_get_campaign(
                advertiser_id=advertiser["advertiser_id"],
                campaign_ids=[ads[0]["campaign_id"]],
            )

            # Get ad group information
            logger.info(
                f"  → Getting ad group information for ID: {ads[0]['adgroup_id']}"
            )
            adgroups = await tiktok_biz_get_adgroup(
                advertiser_id=advertiser["advertiser_id"],
                campaign_ids=[ads[0]["campaign_id"]],
                adgroup_ids=[ads[0]["adgroup_id"]],
            )

            # Create and process report
            report_data = construct_detailed_report(
                report=report,
                advertiser_info=advertiser_info[0] if advertiser_info else {},
                campaign_info=campaigns[0] if campaigns else {},
                adgroup_info=adgroups[0] if adgroups else {},
                ad_info=ads[0] if ads else {},
            )

            logger.debug(report_data)

            doc_id = generate_doc_id(report_data)
            enriched_report = enrich_report(report_data, index_name, doc_id)
            logger.info(enriched_report)

            batch_report.append(enriched_report)
            all_enriched_reports.append(enriched_report)
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

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    # Calculate total spending
    total_spend = sum(float(report.get("spend", 0)) for report in all_enriched_reports)

    return {
        "status": "success",
        "execution_time": execution_time,
        "total_reports": len(all_enriched_reports),
        "total_spend": round(total_spend, 2),
    }
