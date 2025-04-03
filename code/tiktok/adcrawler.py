import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from tiktokadcrawler import TiktokAdCrawler


async def get_reports(
    crawler: TiktokAdCrawler, advertiser_id: str, start_date: str, end_date: str
) -> List[Dict]:
    """
    Fetch advertising reports for a specific advertiser within a date range.

    Args:
        crawler (TiktokAdCrawler): Instance of TiktokAdCrawler
        advertiser_id (str): The ID of the advertiser to fetch reports for
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'

    Returns:
        List[Dict]: List of report entries with metrics and dimensions
    """
    try:
        reports = await crawler.get_integrated_report(
            advertiser_id=advertiser_id, start_date=start_date, end_date=end_date
        )

        if not reports:
            print(f"No reports found for advertiser {advertiser_id}")
            return []

        return reports

    except Exception as e:
        print(f"Error fetching reports: {e}")
        return []


async def main():
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
            print("No advertisers found")
            return

        # For testing, use the last advertiser
        test_advertiser = advertisers[-1]
        advertiser_id = test_advertiser["advertiser_id"]
        print(f"Getting reports for advertiser: {test_advertiser['advertiser_name']}")

        reports = await get_reports(
            crawler=crawler,
            advertiser_id=advertiser_id,
            start_date=start_date,
            end_date=end_date,
        )

        for report in reports:
            print(json.dumps(report, indent=2))

    finally:
        await crawler.session.close()


if __name__ == "__main__":
    asyncio.run(main())
