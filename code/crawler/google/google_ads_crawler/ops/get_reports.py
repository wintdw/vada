import requests
import json
import asyncio
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_refresh_tokens() -> List[str]:
    return ["token1"]


def summarize_report_data(data: Dict) -> None:
    """Log summary of report data including date range, account stats, and campaign metrics"""
    # Extract data
    date_range = data.get("date_range", {})
    account = data.get("account", {})
    report = data.get("report", {})

    # Calculate account stats
    manager_accounts = sum(
        1 for acc in account.get("hierarchy", []) if acc.get("manager", False)
    )
    client_accounts = len(account.get("customer_ads_accounts", []))

    # Log main stats
    logging.info(
        "Report Summary: %s to %s | Accounts: %d managers, %d clients | Campaigns: %d, Ad Groups: %d, Ads: %d, Reports: %d",
        date_range.get("start_date"),
        date_range.get("end_date"),
        manager_accounts,
        client_accounts,
        report.get("total_campaigns", 0),
        report.get("total_ad_groups", 0),
        report.get("total_ads", 0),
        report.get("total_reports", 0),
    )


async def fetch_reports():
    """Test different date ranges for the reports endpoint with multiple tokens"""
    base_url = "http://localhost:8146/google/reports"
    headers = {"Content-Type": "application/json"}

    tokens = get_refresh_tokens()
    logging.info("Starting tests with %d refresh tokens", len(tokens))

    # Use specific date range for production
    start_date = "2024-01-01"
    end_date = "2025-04-30"

    for token_index, refresh_token in enumerate(tokens, 1):
        logging.info("Processing token %d/%d", token_index, len(tokens))
        credentials = {"refresh_token": refresh_token}

        try:
            logging.info(f"Processing data from {start_date} to {end_date}")
            request_data = {
                **credentials,
            }

            # Add dates as query parameters
            params = {"start_date": start_date, "end_date": end_date, "persist": False}

            logging.debug("Making request to %s", base_url)
            response = requests.post(
                base_url, headers=headers, json=request_data, params=params
            )
            response.raise_for_status()

            data = response.json()
            summarize_report_data(data)

            # Save response to file
            output_file = (
                f"googleads_token{token_index}_{start_date}_to_{end_date}.json"
            )

            logging.info("Saving response to %s", output_file)
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

        except requests.RequestException as e:
            logging.error("API request failed for token %d: %s", token_index, str(e))
            if hasattr(e, "response") and e.response is not None:
                logging.error("Error response: %s", e.response.text)
        except Exception as e:
            logging.exception("Unexpected error processing token %d", token_index)


if __name__ == "__main__":
    asyncio.run(fetch_reports())
