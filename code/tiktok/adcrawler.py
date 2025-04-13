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
    Enhance a report with nested dictionaries for advertiser, campaign, ad group and ad.

    Args:
        report (Dict): The original report data
        advertiser_info (Dict): Complete advertiser information
        campaign_info (Dict): Complete campaign information
        adgroup_info (Dict): Complete ad group information
        ad_info (Dict): Complete ad information

    Returns:
        Dict: Enhanced report with nested entity information
    """
    enhanced_report = report.copy()

    # Create nested dictionaries for each entity
    enhanced_report["advertiser"] = advertiser_info
    enhanced_report["campaign"] = campaign_info
    enhanced_report["adgroup"] = adgroup_info
    enhanced_report["ad"] = ad_info

    return enhanced_report


async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    access_token = "xxx"
    app_id = "xxx"
    secret = "xxx"

    start_date = "2025-03-30"
    end_date = "2025-03-31"

    # Define output file path
    output_file = f"tiktok_ads_{start_date}_{end_date}.jsonl"

    crawler = TiktokAdCrawler(access_token, app_id, secret)
    try:
        # Get all advertisers
        advertisers = await crawler.get_advertiser()
        if not advertisers:
            logging.warning("No advertisers found")
            return

        # Loop through all advertisers
        for advertiser in advertisers:
            advertiser_id = advertiser["advertiser_id"]
            logging.info(f"Processing advertiser: {advertiser['advertiser_name']}")

            logging.info("Getting advertiser info")
            advertiser_info = await crawler.get_advertiser_info(advertiser_id)

            logging.info("Getting reports")
            reports = await crawler.get_integrated_report(
                advertiser_id=advertiser_id, start_date=start_date, end_date=end_date
            )
            logging.info(f"Found {len(reports)} reports")

            with open(output_file, "a") as f:
                for report in reports:
                    logging.info("--- Processing new report ---")

                    ad_id = report.get("ad_id")
                    logging.info(f"Found ad_id: {ad_id}")
                    logging.info(f"Getting ads for advertiser_id: {advertiser_id}")

                    ads = await crawler.get_ad(
                        advertiser_id=advertiser_id, ad_ids=[ad_id]
                    )

                    if not ads:
                        logging.warning(f"Warning: No ads found for ad_id {ad_id}")
                        continue

                    campaign_id = ads[0].get("campaign_id")
                    adgroup_id = ads[0].get("adgroup_id")
                    logging.info(
                        f"Found campaign_id: {campaign_id}, adgroup_id: {adgroup_id}"
                    )

                    campaigns = await crawler.get_campaign(
                        advertiser_id=advertiser_id, campaign_ids=[campaign_id]
                    )

                    adgroups = await crawler.get_adgroup(
                        advertiser_id=advertiser_id,
                        campaign_ids=[campaign_id],
                        adgroup_ids=[adgroup_id],
                    )

                    if not campaigns or not adgroups:
                        logging.warning("Missing campaign or adgroup data")
                        continue

                    logging.info("Constructing detailed report with all entity data")
                    detailed_report = construct_detailed_report(
                        report, advertiser_info, campaigns[0], adgroups[0], ads[0]
                    )

                    # Write each report immediately
                    f.write(json.dumps(detailed_report) + "\n")
                    f.flush()  # Ensure the data is written to disk

                    logging.info("Report processing complete")

        logging.info(
            f"Completed processing advertiser: {advertiser['advertiser_name']}. "
            f"Data written to {output_file}"
        )

    finally:
        await crawler.session.close()


if __name__ == "__main__":
    asyncio.run(main())
