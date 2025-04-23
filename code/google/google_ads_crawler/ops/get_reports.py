import requests
import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_refresh_tokens() -> List[str]:
    """Get list of refresh tokens to test"""
    logging.debug("Retrieving refresh tokens")
    return ["token1", "token2"]


def get_test_cases() -> List[Dict]:
    """Get list of test cases with different date ranges"""
    logging.debug("Generating test cases")
    today = datetime.now().date()
    return [
        {
            "params": {
                "start_date": (today - timedelta(days=7)).isoformat(),
                "end_date": today.isoformat(),
            },
            "desc": "Last 7 days reports",
        },
    ]


def summarize_report_data(data: Dict) -> None:
    """Log summary of report data"""
    date_range = data.get("date_range", {})
    accounts = data.get("accounts", {})
    reports = data.get("reports", {})

    logging.info(
        "Report Summary for %s to %s",
        date_range.get("start_date"),
        date_range.get("end_date"),
    )

    logging.info(
        "Account Stats: managers=%d, clients=%d",
        accounts.get("manager_accounts", 0),
        accounts.get("total_clients", 0),
    )

    logging.info(
        "Campaign Stats: campaigns=%d, ad_groups=%d, total_reports=%d",
        reports.get("total_campaigns", 0),
        reports.get("total_ad_groups", 0),
        reports.get("total_reports", 0),
    )

    if reports.get("data"):
        sample = reports["data"][0]
        logging.debug(
            "Sample Record - Customer: %s (%s), Campaign: %s, Ad Group: %s",
            sample.get("customer_name"),
            sample.get("customer_id"),
            sample.get("campaign", {}).get("name"),
            sample.get("ad_group", {}).get("name"),
        )

        logging.debug(
            "Sample Metrics - Cost: %.2f, Clicks: %d, Impressions: %d, Conversions: %.2f",
            sample.get("cost", 0),
            sample.get("clicks", 0),
            sample.get("impressions", 0),
            sample.get("conversions", 0),
        )


def process_json_to_jsonl(input_file: str, index_name: str) -> None:
    """Process JSON file to JSONL with VADA ingest configuration"""
    # Get base filename without extension for output
    base_name = input_file.rsplit(".", 1)[0]
    output_file = f"{base_name}.jsonl"

    logging.info(f"Processing {input_file} to {output_file}")

    with open(input_file, "r") as f:
        data = json.load(f)

    # Process each report record
    records = data.get("reports", {}).get("data", [])
    with open(output_file, "w") as f:
        for record in records:
            # Generate doc_id from ad, adgroup, campaign IDs and date
            ad_id = record.get("ad", {}).get("id", "")
            adgroup_id = record.get("ad_group", {}).get("id", "")
            campaign_id = record.get("campaign", {}).get("id", "")
            date = record.get("date", "")

            doc_id = f"{ad_id}.{adgroup_id}.{campaign_id}_{date}"

            # Add VADA configuration
            record["_vada"] = {
                "ingest": {
                    "destination": {"type": "elasticsearch", "index": index_name},
                    "vada_client_id": "a_quang_nguyen",
                    "doc_id": doc_id,
                }
            }

            # Write each record as a single line
            f.write(json.dumps(record) + "\n")

    logging.info(f"Created JSONL file: {output_file}")
    logging.info(f"Processed {len(records)} records")


async def test_reports_endpoint():
    """Test different date ranges for the reports endpoint with multiple tokens"""
    base_url = "http://localhost:8146/google/reports"
    headers = {"Content-Type": "application/json"}

    tokens = get_refresh_tokens()
    logging.info("Starting tests with %d refresh tokens", len(tokens))

    for token_index, refresh_token in enumerate(tokens, 1):
        logging.info("Processing token %d/%d", token_index, len(tokens))
        credentials = {"refresh_token": refresh_token}

        for test_case in get_test_cases():
            try:
                logging.info("Running test case: %s", test_case["desc"])
                request_data = {**credentials, **test_case["params"]}

                logging.debug("Making request to %s", base_url)
                response = requests.post(base_url, headers=headers, json=request_data)
                response.raise_for_status()

                data = response.json()
                summarize_report_data(data)

                # Save response to file
                start_date = data["date_range"]["start_date"]
                end_date = data["date_range"]["end_date"]
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
                logging.error(
                    "API request failed for token %d: %s", token_index, str(e)
                )
                if hasattr(e, "response") and e.response is not None:
                    logging.error("Error response: %s", e.response.text)
            except Exception as e:
                logging.exception("Unexpected error processing token %d", token_index)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_reports_endpoint())
