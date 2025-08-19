import asyncio
import logging
from typing import Dict

from service.oauth import tiktok_biz_get_advertiser
from service.tiktok import (
    tiktok_biz_info_advertiser,
    tiktok_biz_get_report_integrated,
    tiktok_biz_get_ad,
    tiktok_biz_get_campaign,
    tiktok_biz_get_adgroup,
    tiktok_biz_get_gmv_max_campaign_detail,
)


def construct_detailed_report(
    report: Dict,
    advertiser_info: Dict,
    campaign_info: Dict,
    adgroup_info: Dict,
    ad_info: Dict,
    gmv_max_info: Dict,
) -> Dict:
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
    enhanced_report["gmv_max"] = gmv_max_info

    return enhanced_report


async def crawl_tiktok_business(
    access_token: str, start_date: str, end_date: str
) -> Dict:
    try:
        # Get all advertisers
        advertisers = await tiktok_biz_get_advertiser(access_token)
        total_advertisers = len(advertisers)
        logging.debug(f"Found {total_advertisers} advertisers to process")
        logging.debug(advertisers)

        detailed_reports = []

        for idx, advertiser in enumerate(advertisers, 1):
            logging.debug(
                f"Processing advertiser {idx}/{total_advertisers} - ID: {advertiser['advertiser_id']}"
            )

            # Get advertiser info
            advertiser_info = await tiktok_biz_info_advertiser(
                access_token, [advertiser["advertiser_id"]]
            )
            logging.debug(
                f"  → Advertiser name: {advertiser_info[0].get('name', 'N/A')}"
            )
            logging.debug(advertiser_info)

            # Get integrated report
            reports = await tiktok_biz_get_report_integrated(
                access_token=access_token,
                advertiser_id=advertiser["advertiser_id"],
                start_date=start_date,
                end_date=end_date,
            )
            total_reports = len(reports)
            logging.debug(f"  → Found {total_reports} reports for this advertiser")

            for report_idx, report in enumerate(reports, 1):
                logging.debug(f"  → Processing report {report_idx}/{total_reports}")
                logging.debug(f"    • Ad ID: {report.get('ad_id')}")
                logging.debug(f"    • Date: {report.get('stat_time_day')}")
                logging.debug(f"    • Spend: {report.get('spend', '0')}")

                if float(report.get("spend", "0")) == 0:
                    logging.debug("    ✗ Skipping report with zero spend")
                    continue

                # Get ad information
                logging.debug(
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

                gmv_max_task = asyncio.create_task(
                    tiktok_biz_get_gmv_max_campaign_detail(
                        access_token=access_token,
                        advertiser_id=advertiser["advertiser_id"],
                        campaign_id=ads[0]["campaign_id"],
                    )
                )

                # Wait for both tasks to complete
                campaigns, adgroups, gmv_max_info = await asyncio.gather(
                    campaign_task, adgroup_task, gmv_max_task
                )

                # Create and process report
                detailed_report = construct_detailed_report(
                    report=report,
                    advertiser_info=advertiser_info[0] if advertiser_info else {},
                    campaign_info=campaigns[0] if campaigns else {},
                    adgroup_info=adgroups[0] if adgroups else {},
                    ad_info=ads[0] if ads else {},
                    gmv_max_info=gmv_max_info,
                )

                detailed_reports.append(detailed_report)

        # Send reports in batches
        total_reports = len(detailed_reports)

        if total_reports == 0:
            # Do not send batch to Datastore if no reports
            return {
                "status": "success",
                "date_start": start_date,
                "date_end": end_date,
                "report": {
                    "total_reports": 0,
                    "total_spend": 0.0,
                    "reports": [],
                },
            }

        # Calculate total spending
        total_spend = sum(float(report.get("spend", 0)) for report in detailed_reports)

        return {
            "status": "success",
            "date_start": start_date,
            "date_end": end_date,
            "report": {
                "total_reports": total_reports,
                "total_spend": round(total_spend, 2),
                "reports": detailed_reports,
            },
        }
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        raise Exception(f"Failed to crawl TikTok business data: {str(e)}")
