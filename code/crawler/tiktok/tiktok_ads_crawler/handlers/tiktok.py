import json


def construct_detailed_report(
    report: dict,
    advertiser_info: dict,
    campaign_info: dict,
    adgroup_info: dict,
    ad_info: dict,
) -> dict:
    """
    Enhance a report with nested dictionaries for advertiser, campaign, ad group and ad.

    Args:
        report (dict): The original report data
        advertiser_info (dict): Complete advertiser information
        campaign_info (dict): Complete campaign information
        adgroup_info (dict): Complete ad group information
        ad_info (dict): Complete ad information

    Returns:
        dict: Enhanced report with nested entity information
    """
    enhanced_report = report.copy()

    # Create nested dictionaries for each entity
    enhanced_report["advertiser"] = advertiser_info
    enhanced_report["campaign"] = campaign_info
    enhanced_report["adgroup"] = adgroup_info
    enhanced_report["ad"] = ad_info

    return enhanced_report


def save_report(data, filename):
    with open(filename, "a", encoding="utf-8") as f:  # Changed "a" to "w"
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")


def enrich_report(report: dict, index_name: str, doc_id: str) -> dict:
    metadata = {
        "_vada": {
            "ingest": {
                "destination": {"type": "elasticsearch", "index": index_name},
                "vada_client_id": "a_quang_nguyen",
                "doc_id": doc_id,
            }
        }
    }
    return report | metadata


def enrich_anchi_report(enriched_report: dict) -> dict:
    """
    Enrich report with vada metadata for ANCHI GROUP VIET NAM JOINT STOCK COMPANY.
    
    Args:
        enriched_report (dict): The enriched report with advertiser information
        
    Returns:
        dict: Report with additional vada metadata if applicable
    """
    # Check if advertiser company is ANCHI GROUP VIET NAM JOINT STOCK COMPANY
    advertiser = enriched_report.get("advertiser", {})
    company = advertiser.get("company", "")
    
    if company != "ANCHI GROUP VIET NAM JOINT STOCK COMPANY":
        return enriched_report
    
    # Parse advertiser name (format: AF-TT-NS016-2)
    advertiser_name = advertiser.get("name", "")
    
    if not advertiser_name or "-" not in advertiser_name:
        return enriched_report
    
    try:
        # Split the name by hyphens
        parts = advertiser_name.split("-")
        
        if len(parts) >= 4:
            ma_du_an = parts[0]  # AF
            kenh_quang_cao = parts[1]  # TT
            marketer_id = parts[2]  # NS016
            sub_account_name = parts[3]  # 2
            
            # Create vada metadata
            vada_metadata = {
                "vada": {
                    "ma_du_an": ma_du_an,
                    "kenh_quang_cao": kenh_quang_cao,
                    "marketer_id": marketer_id,
                    "sub_account_name": sub_account_name
                }
            }
            
            # Add vada metadata to the report
            return enriched_report | vada_metadata
        else:
            return enriched_report
            
    except Exception:
        # If parsing fails, return the original report
        return enriched_report

async def crawl_tiktok_business(index_name: str, access_token: str, start_date: str, end_date: str):
    import logging
    import time
    import uuid
    import asyncio
    from datetime import datetime
    from fastapi import HTTPException  # type: ignore
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
    from .insert import add_insert_metadata

    logger = get_logger(__name__, logging.INFO)

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

        batch_size = 1000
        all_enriched_reports = []

        for idx, advertiser in enumerate(advertisers, 1):
            logger.debug(
                f"Processing advertiser {idx}/{total_advertisers} - ID: {advertiser['advertiser_id']}"
            )

            # Get advertiser info
            advertiser_info = await tiktok_biz_info_advertiser(
                access_token,
                [advertiser["advertiser_id"]]
            )
            logger.debug(f"  → Advertiser name: {advertiser_info[0].get('name', 'N/A')}")
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
                    advertiser_id=advertiser["advertiser_id"], ad_ids=[report["ad_id"]]
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
                logger.debug(enriched_report)

                enriched_anchi_report = enrich_anchi_report(enriched_report)
                logger.debug(enriched_anchi_report)

                all_enriched_reports.append(enriched_anchi_report)
                save_report(enriched_anchi_report, "report.jsonl")

        # Send reports in batches
        total_reports = len(all_enriched_reports)
        logger.debug(f"Sending {total_reports} reports in batches of {batch_size}")

        for i in range(0, total_reports, batch_size):
            batch = all_enriched_reports[i : i + batch_size]
            current_batch = i // batch_size + 1
            total_batches = (total_reports + batch_size - 1) // batch_size

            logger.debug(f"Sending batch {current_batch} of {total_batches}")
            insert_json = await send_to_insert_service(
                add_insert_metadata(batch, index_name)
            )

            status = insert_json.get("status", "unknown")
            detail = insert_json.get("detail", "no details provided")
            logger.debug(
                f"Batch {current_batch}/{total_batches} - Status: {status} - Detail: {detail}"
            )

            if status != "success":
                logger.error(f"Failed to insert batch {current_batch}: {detail}")

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)

        # Calculate total spending
        total_spend = sum(float(report.get("spend", 0)) for report in all_enriched_reports)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
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