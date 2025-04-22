import requests
import json
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_refresh_tokens() -> List[str]:
    """Get list of refresh tokens to test"""
    return ["token1", "token2"]


def get_test_cases() -> List[Dict]:
    """Get list of test cases with different date ranges"""
    return [
        {"params": {"days": 1}, "desc": "Last 1 days reports"},
        {"params": {"days": 3}, "desc": "Last 3 days reports"},
        {"params": {"days": 7}, "desc": "Last 7 days reports"},
    ]


def summarize_report_data(data: Dict) -> None:
    """Log summary of report data"""
    date_range = data.get("date_range", {})
    accounts = data.get("accounts", {})
    reports = data.get("reports", {})

    logger.info("\nReport Summary:")
    logger.info(
        f"Date Range: {date_range.get('start_date')} to {date_range.get('end_date')}"
    )
    logger.info(f"Manager Accounts: {accounts.get('manager_accounts', 0)}")
    logger.info(f"Total Clients: {accounts.get('total_clients', 0)}")
    logger.info(f"Total Campaigns: {reports.get('total_campaigns', 0)}")
    logger.info(f"Total Ad Groups: {reports.get('total_ad_groups', 0)}")
    logger.info(f"Total Records: {reports.get('total_records', 0)}")

    # Log sample data if available
    if reports.get("data"):
        sample = reports["data"][0]
        logger.info("\nSample Record:")
        logger.info(
            f"  Customer: {sample.get('customer_name')} ({sample.get('customer_id')})"
        )
        logger.info(f"  Campaign: {sample.get('campaign', {}).get('name')}")
        logger.info(f"  Ad Group: {sample.get('ad_group', {}).get('name')}")
        logger.info(f"  Metrics:")
        logger.info(f"    Cost: {sample.get('cost', 0):.2f}")
        logger.info(f"    Clicks: {sample.get('clicks', 0)}")
        logger.info(f"    Impressions: {sample.get('impressions', 0)}")
        logger.info(f"    Conversions: {sample.get('conversions', 0):.2f}")


async def test_reports_endpoint():
    """Test different date ranges for the reports endpoint with multiple tokens"""

    base_url = "http://localhost:8146/google/reports"
    headers = {"Content-Type": "application/json"}

    for token_index, refresh_token in enumerate(get_refresh_tokens(), 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing with refresh token #{token_index}")
        logger.info("=" * 50)

        credentials = {"refresh_token": refresh_token}

        for test_case in get_test_cases():
            try:
                logger.info(f"\nTesting: {test_case['desc']}")

                response = requests.post(
                    base_url,
                    headers=headers,
                    params=test_case["params"],
                    json=credentials,
                )

                response.raise_for_status()

                # Log success and summary
                logger.info(f"Status Code: {response.status_code}")
                data = response.json()

                # Log summary of the response
                summarize_report_data(data)

                # Save detailed response to file
                output_file = f"report_response_token{token_index}_{test_case['params']['days']}days.json"
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info(f"\nFull response saved to: {output_file}")

            except requests.RequestException as e:
                logger.error(f"Error with token #{token_index}: {str(e)}")
                if hasattr(e, "response") and e.response is not None:
                    logger.error(f"Error response: {e.response.text}")

            logger.info("-" * 50)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_reports_endpoint())
