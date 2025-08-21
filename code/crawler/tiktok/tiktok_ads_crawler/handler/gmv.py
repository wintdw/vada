import asyncio
import logging
from typing import Dict

from service.oauth import tiktok_biz_get_advertisers
from service.gmv import (
    get_gmv_max_campaigns,
    tiktok_biz_get_gmv_max_campaign_detail,
)


async def crawl_tiktok_gmv_campaigns(
    access_token: str, start_date: str, end_date: str
) -> Dict:
    try:
        # Get all advertisers
        advertisers = await tiktok_biz_get_advertisers(access_token)
        total_advertisers = len(advertisers)
        logging.debug(f"Found {total_advertisers} advertisers to process")
        logging.debug(advertisers)

        detailed_campaigns = []

        for idx, advertiser in enumerate(advertisers, 1):
            advertiser_id = advertiser["advertiser_id"]
            logging.debug(
                f"Processing advertiser {idx}/{total_advertisers} - ID: {advertiser_id}"
            )

            # Get all GMV Max campaigns for this advertiser
            campaigns = await get_gmv_max_campaigns(
                access_token=access_token,
                advertiser_id=advertiser_id,
                date_start=start_date,
                date_end=end_date,
            )
            total_campaigns = len(campaigns)
            logging.debug(
                f"  → Found {total_campaigns} GMV Max campaigns for this advertiser"
            )

            # Gather campaign details in parallel
            tasks = [
                tiktok_biz_get_gmv_max_campaign_detail(
                    access_token=access_token,
                    advertiser_id=advertiser_id,
                    campaign_id=campaign["campaign_id"],
                )
                for campaign in campaigns
            ]
            if tasks:
                campaign_details = await asyncio.gather(*tasks)
                detailed_campaigns.extend(campaign_details)

        total_campaigns = len(detailed_campaigns)
        if total_campaigns == 0:
            return {
                "status": "success",
                "date_start": start_date,
                "date_end": end_date,
                "campaigns": [],
                "total_campaigns": 0,
            }

        return {
            "status": "success",
            "date_start": start_date,
            "date_end": end_date,
            "campaigns": detailed_campaigns,
            "total_campaigns": total_campaigns,
        }
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        raise Exception(f"Failed to crawl TikTok GMV Max campaigns: {str(e)}")
