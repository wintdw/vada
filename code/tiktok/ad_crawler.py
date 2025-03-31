import asyncio
import json
import hashlib
from typing import Dict, List

from tiktokadcrawler import TiktokAdCrawler


def generate_docid(doc: Dict) -> str:
    """
    Generates a unique document ID based on the serialized dictionary.

    Args:
        doc (Dict): The dictionary to generate the ID for.

    Returns:
        str: The generated document ID.
    """
    serialized_data = json.dumps(doc, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def append_metadata(data: List[Dict], metadata: Dict) -> List[Dict]:
    """
    Appends metadata to each dictionary in the list and generates a unique doc_id for each record.

    Args:
        data (List[Dict]): The list of dictionaries to process.
        metadata (Dict): The metadata to append to each dictionary.

    Returns:
        List[Dict]: The updated list of dictionaries with metadata and unique doc_id.
    """
    updated_data = []
    for record in data:
        # Generate a unique doc_id for the record
        doc_id = generate_docid(record)

        # Create a copy of metadata to avoid modifying the original
        record_metadata = {
            **metadata,
            "ingest": {**metadata["ingest"], "doc_id": doc_id},
        }

        # Merge the record with the metadata
        record_with_metadata = {**record, "_vada": record_metadata}
        updated_data.append(record_with_metadata)

    return updated_data


def write_to_jsonl(file_path: str, data: List[Dict], append: bool = False) -> None:
    """
    Writes a list of dictionaries to a JSONL file.

    Args:
        file_path (str): The path to the JSONL file.
        data (List[Dict]): The list of dictionaries to write.
        append (bool): If True, append to file; if False, overwrite. Default is False.
    """
    mode = "a" if append else "w"
    with open(file_path, mode) as file:
        for record in data:
            file.write(json.dumps(record, sort_keys=True) + "\n")


# Example usage
async def main():
    access_token = "xxx"
    app_id = "xxx"
    secret = "xxx"

    ads_jsonl_file = "tiktok_ads.jsonl"
    reports_jsonl_file = "tiktok_ad_reports.jsonl"
    start_date = "2025-03-01"
    end_date = "2025-03-31"

    metadata = {
        "ingest": {
            "source": "crawling:tiktok_ad",
            "destination": {
                "type": "elasticsearch",
                "index": "a_quang_nguyen_tiktok_ad",
            },
            "vada_client_id": "a_quang_nguyen",
            "type": "tiktok_ad",
        }
    }

    report_metadata = {
        "ingest": {
            "source": "crawling:tiktok_ad_report",
            "destination": {
                "type": "elasticsearch",
                "index": "a_quang_nguyen_tiktok_ad_report",
            },
            "vada_client_id": "a_quang_nguyen",
            "type": "tiktok_ad_report",
        }
    }

    tiktok_crawler: TiktokAdCrawler = TiktokAdCrawler(access_token, app_id, secret)

    try:
        advertisers: Dict = await tiktok_crawler.get_advertisers()
        if (
            advertisers
            and "data" in advertisers
            and "list" in advertisers["data"]
            and len(advertisers["data"]["list"]) > 0
        ):
            total_ads = 0
            total_reports = 0

            # Write headers to new files
            write_to_jsonl(ads_jsonl_file, [])
            write_to_jsonl(reports_jsonl_file, [])

            # Iterate through all advertisers
            for advertiser in advertisers["data"]["list"]:
                advertiser_id: str = advertiser["advertiser_id"]
                print(f"Fetching ads for advertiser: {advertiser_id}")

                # Get advertiser info
                advertiser_info = await tiktok_crawler.get_advertiser_info(
                    advertiser_id
                )
                advertiser_name = (
                    (
                        advertiser_info.get("data", {})
                        .get("list", [{}])[0]
                        .get("name", "unknown")
                    )
                    if advertiser_info
                    else "unknown"
                )

                ads = await tiktok_crawler.get_ad(advertiser_id)

                if ads:
                    # Process and write ads for this advertiser
                    updated_ads = append_metadata(ads, metadata)
                    write_to_jsonl(ads_jsonl_file, updated_ads, append=True)
                    total_ads += len(ads)
                    print(f"Wrote {len(ads)} ads for advertiser {advertiser_id}")

                    # Fetch reports for each ad
                    print(f"Fetching reports for advertiser: {advertiser_id}")
                    report = await tiktok_crawler.get_integrated_report(
                        advertiser_id=advertiser_id,
                        start_date=start_date,
                        end_date=end_date,
                    )

                    if report and "data" in report and "list" in report["data"]:
                        # Flatten the report data
                        flattened_reports = []
                        for item in report["data"]["list"]:
                            flattened_item = {
                                "advertiser_id": advertiser_id,
                                "advertiser_name": advertiser_name,  # Add advertiser name
                                **item["dimensions"],  # Unpack dimensions
                                **item["metrics"],  # Unpack metrics
                            }
                            flattened_reports.append(flattened_item)

                        updated_reports = append_metadata(
                            flattened_reports, report_metadata
                        )
                        write_to_jsonl(reports_jsonl_file, updated_reports, append=True)
                        total_reports += len(report["data"]["list"])

            print(f"Ad information written to {ads_jsonl_file}")
            print(f"Report information written to {reports_jsonl_file}")
            print(f"Total ads collected: {total_ads}")
            print(f"Total reports collected: {total_reports}")
        else:
            print("No advertiser information found.")
    finally:
        await tiktok_crawler.session.close()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
