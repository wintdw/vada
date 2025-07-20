import time
import uuid
import asyncio

from datetime import datetime
from fastapi import HTTPException  # type: ignore

from tools.logger import get_logger, request_id
from .enrichment import construct_detailed_report, enrich_report
from .persist import send_batch
from services.tiktok import (
    tiktok_biz_get_advertiser,
    tiktok_biz_info_advertiser,
    tiktok_biz_get_report_integrated,
    tiktok_biz_get_ad,
    tiktok_biz_get_campaign,
    tiktok_biz_get_adgroup,
)

logger = get_logger(__name__)


async def crawl_tiktok_business(
    index_name: str, access_token: str, start_date: str, end_date: str
):
    # Generate and set request ID at the start of each request
    req_id = str(uuid.uuid4())[:8]  # Take first 8 characters
    request_id.set(req_id)
    start_time = time.time()

    try:
        # Get all advertisers
        advertisers = await tiktok_biz_get_advertiser(access_token)
        total_advertisers = len(advertisers)
        logger.debug(f"Found {total_advertisers} advertisers to process")
        logger.debug(advertisers)

        all_enriched_reports = []

        for idx, advertiser in enumerate(advertisers, 1):
            logger.debug(
                f"Processing advertiser {idx}/{total_advertisers} - ID: {advertiser['advertiser_id']}"
            )

            # Get advertiser info
            advertiser_info = await tiktok_biz_info_advertiser(
                access_token, [advertiser["advertiser_id"]]
            )
            logger.debug(
                f"  → Advertiser name: {advertiser_info[0].get('name', 'N/A')}"
            )
            logger.debug(advertiser_info)

            # Get integrated report
            reports = await tiktok_biz_get_report_integrated(
                access_token=access_token,
                advertiser_id=advertiser["advertiser_id"],
                start_date=start_date,
                end_date=end_date,
            )
            total_reports = len(reports)
            logger.debug(f"  → Found {total_reports} reports for this advertiser")
            logger.debug(reports)

            for report_idx, report in enumerate(reports, 1):
                logger.debug(f"  → Processing report {report_idx}/{total_reports}")
                logger.debug(f"    • Ad ID: {report.get('ad_id')}")
                logger.debug(f"    • Date: {report.get('stat_time_day')}")
                logger.debug(f"    • Spend: {report.get('spend', '0')}")

                if float(report.get("spend", "0")) == 0:
                    logger.debug("    ✗ Skipping report with zero spend")
                    continue

                # Get ad information
                logger.debug(
                    f"  → Getting campaign / adgroup / ad information for Ad ID: {report['ad_id']}"
                )
                ads = await tiktok_biz_get_ad(
                    access_token=access_token,
                    advertiser_id=advertiser["advertiser_id"],
                    ad_ids=[report["ad_id"]],
                )

                # Create tasks for campaign and adgroup in parallel
                campaign_task = asyncio.create_task(
                    tiktok_biz_get_campaign(
                        access_token=access_token,
                        advertiser_id=advertiser["advertiser_id"],
                        campaign_ids=[ads[0]["campaign_id"]],
                    )
                )

                adgroup_task = asyncio.create_task(
                    tiktok_biz_get_adgroup(
                        access_token=access_token,
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
                all_enriched_reports.append(enriched_report)

        # Send reports in batches
        total_reports = len(all_enriched_reports)
        send_batches = await send_batch(
            batch_report=all_enriched_reports, index_name=index_name
        )

        # Log the response from the insert service
        logger.debug(
            f"Send {total_reports} reports to Datastore: {send_batches['status']} - {send_batches.get('detail', '')}"
        )

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)

        # Calculate total spending
        total_spend = sum(
            float(report.get("spend", 0)) for report in all_enriched_reports
        )
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )

    return {
        "status": "success",
        "execution_time": execution_time,
        "total_reports": total_reports,
        "total_spend": round(total_spend, 2),
        "date_start": start_date,
        "date_end": end_date,
    }
