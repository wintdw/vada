import logging
import time
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter  # type: ignore
from tools import get_logger, request_id

from services import (
    tiktok_biz_get_advertiser,
    tiktok_biz_info_advertiser,
    tiktok_biz_get_report_integrated,
    tiktok_biz_get_ad,
    tiktok_biz_get_campaign,
    tiktok_biz_get_adgroup,
    send_to_insert_service,
)
from handlers import (
    construct_detailed_report,
    save_report,
    enrich_report,
    add_insert_metadata,
)

router = APIRouter()
logger = get_logger(__name__, logging.INFO)


@router.get("/v1/tiktok_business/get/", tags=["Tiktok"])
async def tiktok_business_get(index_name: str, access_token: str, start_date: str, end_date: str):
    # Generate and set request ID at the start of each request
    req_id = str(uuid.uuid4())[:8]  # Take first 8 characters
    request_id.set(req_id)

    start_time = time.time()

    # Get all advertisers
    advertisers = await tiktok_biz_get_advertiser(access_token)
    total_advertisers = len(advertisers)
    logger.info(f"Found {total_advertisers} advertisers to process")
    logger.debug(advertisers)

    batch_size = 1000
    all_enriched_reports = []

    for idx, advertiser in enumerate(advertisers, 1):
        logger.info(
            f"Processing advertiser {idx}/{total_advertisers} - ID: {advertiser['advertiser_id']}"
        )

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
        total_reports = len(reports)
        logger.info(f"  → Found {total_reports} reports for this advertiser")
        logger.debug(reports)

        for report_idx, report in enumerate(reports, 1):
            logger.info(f"  → Processing report {report_idx}/{total_reports}")
            logger.info(f"    • Ad ID: {report.get('ad_id')}")
            logger.info(f"    • Date: {report.get('stat_time_day')}")
            logger.info(f"    • Spend: {report.get('spend', '0')}")

            if float(report.get("spend", "0")) == 0:
                logger.info("    ✗ Skipping report with zero spend")
                continue

            # Get ad information
            logger.info(
                f"  → Getting campaign / adgroup / ad information for Ad ID: {report['ad_id']}"
            )
            ads = await tiktok_biz_get_ad(
                advertiser_id=advertiser["advertiser_id"], ad_ids=[report["ad_id"]]
            )

            # Create tasks for campaign and adgroup in parallel
            campaign_task = asyncio.create_task(
                tiktok_biz_get_campaign(
                    advertiser_id=advertiser["advertiser_id"],
                    campaign_ids=[ads[0]["campaign_id"]],
                )
            )

            adgroup_task = asyncio.create_task(
                tiktok_biz_get_adgroup(
                    advertiser_id=advertiser["advertiser_id"],
                    campaign_ids=[ads[0]["campaign_id"]],
                    adgroup_ids=[ads[0]["adgroup_id"]],
                )
            )

            # Wait for both tasks to complete
            campaigns, adgroups = await asyncio.gather(campaign_task, adgroup_task)

            # Create and process report
            detailed_report = construct_detailed_report(
                report=report,
                advertiser_info=advertiser_info[0] if advertiser_info else {},
                campaign_info=campaigns[0] if campaigns else {},
                adgroup_info=adgroups[0] if adgroups else {},
                ad_info=ads[0] if ads else {},
            )

            timestamp = int(
                datetime.strptime(
                    report["stat_time_day"], "%Y-%m-%d %H:%M:%S"
                ).timestamp()
            )
            doc_id = f"{report['ad_id']}_{timestamp}"
            enriched_report = enrich_report(detailed_report, index_name, doc_id)
            logger.info(enriched_report)

            all_enriched_reports.append(enriched_report)
            save_report(enriched_report, "report.jsonl")

    # Send reports in batches
    total_reports = len(all_enriched_reports)
    logger.info(f"Sending {total_reports} reports in batches of {batch_size}")

    for i in range(0, total_reports, batch_size):
        batch = all_enriched_reports[i : i + batch_size]
        current_batch = i // batch_size + 1
        total_batches = (total_reports + batch_size - 1) // batch_size

        logger.info(f"Sending batch {current_batch} of {total_batches}")
        insert_json = await send_to_insert_service(
            add_insert_metadata(batch, index_name)
        )

        status = insert_json.get("status", "unknown")
        detail = insert_json.get("detail", "no details provided")
        logger.info(
            f"Batch {current_batch}/{total_batches} - Status: {status} - Detail: {detail}"
        )

        if status != "success":
            logger.error(f"Failed to insert batch {current_batch}: {detail}")

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    # Calculate total spending
    total_spend = sum(float(report.get("spend", 0)) for report in all_enriched_reports)

    return {
        "status": "success",
        "execution_time": execution_time,
        "total_reports": total_reports,
        "total_spend": round(total_spend, 2),
        "date_start": start_date,
        "date_end": end_date,
    }
