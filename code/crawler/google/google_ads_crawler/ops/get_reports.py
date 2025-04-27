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
    accounts = data.get("accounts", {})
    reports = data.get("reports", {})

    # Log main stats
    logging.info(
        "Report Summary: %s to %s | Accounts: %d managers, %d clients | Campaigns: %d, Ad Groups: %d, Reports: %d",
        date_range.get("start_date"),
        date_range.get("end_date"),
        accounts.get("manager_accounts", 0),
        accounts.get("total_clients", 0),
        reports.get("total_campaigns", 0),
        reports.get("total_ad_groups", 0),
        reports.get("total_reports", 0),
    )

    # Log sample record if available
    if records := reports.get("data"):
        sample = records[0]
        logging.debug(
            "Sample: Customer=%s (%s) | Campaign=%s | AdGroup=%s | Metrics: Cost=%.2f, Clicks=%d, Impressions=%d, Conv=%.2f",
            sample.get("customer_name"),
            sample.get("customer_id"),
            sample.get("campaign", {}).get("name"),
            sample.get("ad_group", {}).get("name"),
            sample.get("cost", 0),
            sample.get("clicks", 0),
            sample.get("impressions", 0),
            sample.get("conversions", 0),
        )


def process_json_to_jsonl(input_file: str, index_name: str) -> None:
    """Convert JSON report data to JSONL format with VADA ingest configuration"""
    output_file = f"{input_file.rsplit('.', 1)[0]}.jsonl"
    logging.info(f"Converting {input_file} to {output_file}")

    with open(input_file) as f:
        records = json.load(f).get("reports", {}).get("data", [])

    with open(output_file, "w") as f:
        for record in records:
            # Create doc_id from record identifiers
            doc_id = ".".join(
                [
                    str(record.get("ad", {}).get("id", "")),
                    str(record.get("ad_group", {}).get("id", "")),
                    str(record.get("campaign", {}).get("id", "")),
                    str(record.get("date", "")),
                ]
            )

            # Add VADA configuration
            record["_vada"] = {
                "ingest": {
                    "destination": {"type": "elasticsearch", "index": index_name},
                    "vada_client_id": "a_quang_nguyen",
                    "doc_id": doc_id,
                }
            }
            f.write(json.dumps(record) + "\n")

    logging.info(f"Processed {len(records)} records to {output_file}")


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
            params = {"start_date": start_date, "end_date": end_date}

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

            # Process JSONL
            index_name = "a_quang_nguyen_google_ad_report"
            logging.info("Processing to JSONL with index: %s", index_name)
            process_json_to_jsonl(output_file, index_name)

        except requests.RequestException as e:
            logging.error("API request failed for token %d: %s", token_index, str(e))
            if hasattr(e, "response") and e.response is not None:
                logging.error("Error response: %s", e.response.text)
        except Exception as e:
            logging.exception("Unexpected error processing token %d", token_index)


if __name__ == "__main__":
    asyncio.run(fetch_reports())
