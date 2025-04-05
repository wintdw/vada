import logging
import asyncio
import json
from typing import Dict, List
from tiktokadcrawler import TiktokAdCrawler


def construct_detailed_report(
    report: Dict,
    advertiser_info: Dict,
    campaign_info: Dict,
    adgroup_info: Dict,
    ad_info: Dict,
) -> Dict:
    """
    Enhance a report with all available information from advertiser, campaign, ad group and ad.

    Args:
        report (Dict): The original report data
        advertiser_info (Dict): Complete advertiser information
        campaign_info (Dict): Complete campaign information
        adgroup_info (Dict): Complete ad group information
        ad_info (Dict): Complete ad information

    Returns:
        Dict: Enhanced report with all entity information
    """
    enhanced_report = report.copy()

    # Add all fields from each entity with appropriate prefixes
    for key, value in advertiser_info.items():
        enhanced_report[f"advertiser_{key}"] = value

    for key, value in campaign_info.items():
        enhanced_report[f"campaign_{key}"] = value

    for key, value in adgroup_info.items():
        enhanced_report[f"adgroup_{key}"] = value

    for key, value in ad_info.items():
        enhanced_report[f"ad_{key}"] = value

    return enhanced_report


async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    access_token = "xxx"
    app_id = "xxx"
    secret = "xxx"

    start_date = "2025-03-01"
    end_date = "2025-03-31"

    crawler = TiktokAdCrawler(access_token, app_id, secret)
    try:
        # Get all advertisers
        advertisers = await crawler.get_advertiser()
        if not advertisers:
            logging.warning("No advertisers found")
            return

        # For testing, use the last advertiser
        test_advertiser = advertisers[-1]
        advertiser_id = test_advertiser["advertiser_id"]

        logging.info(
            f"Getting advertiser info for: {test_advertiser['advertiser_name']}"
        )
        advertiser_info = await crawler.get_advertiser_info(advertiser_id)

        logging.info(
            f"Getting reports for advertiser: {test_advertiser['advertiser_name']}"
        )
        reports = await crawler.get_integrated_report(
            advertiser_id=advertiser_id, start_date=start_date, end_date=end_date
        )

        # Construct detailed reports
        detailed_reports = []

        for report in reports:
            logging.info("--- Processing new report ---")

            ad_id = report.get("ad_id")
            logging.info(f"Found ad_id: {ad_id}")
            logging.info(f"Getting ads for advertiser_id: {advertiser_id}")

            ads = await crawler.get_ad(advertiser_id=advertiser_id, ad_ids=[ad_id])
            logging.info(f"Retrieved {len(ads)} ads")

            if not ads:
                logging.warning(f"Warning: No ads found for ad_id {ad_id}")
                continue

            campaign_id = ads[0].get("campaign_id")
            adgroup_id = ads[0].get("adgroup_id")
            logging.info(f"Found campaign_id: {campaign_id}, adgroup_id: {adgroup_id}")

            campaigns = await crawler.get_campaign(
                advertiser_id=advertiser_id, campaign_ids=[campaign_id]
            )
            logging.info(f"Retrieved {len(campaigns)} campaigns")

            adgroups = await crawler.get_adgroup(
                advertiser_id=advertiser_id,
                campaign_ids=[campaign_id],
                adgroup_ids=[adgroup_id],
            )
            logging.info(f"Retrieved {len(adgroups)} ad groups")

            if not campaigns or not adgroups:
                logging.warning("Missing campaign or adgroup data")
                continue

            logging.info("Constructing detailed report with all entity data")
            detailed_reports.append(
                construct_detailed_report(
                    report, advertiser_info, campaigns[0], adgroups[0], ads[0]
                )
            )
            logging.info("Report processing complete")

        for report in detailed_reports:
            logging.info(json.dumps(report, indent=2))

    finally:
        await crawler.session.close()


if __name__ == "__main__":
    asyncio.run(main())
