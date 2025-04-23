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


async def get_ad_details(tiktok_crawler: TiktokAdCrawler, ad_id: str) -> Dict:
    """
    Get detailed information for a specific ad including its adgroup and campaign info.
    """
    ad_info = await tiktok_crawler.get_ad(ad_id=ad_id)
    if not ad_info or not ad_info.get("data", {}).get("list"):
        return {}

    ad = ad_info["data"]["list"][0]
    adgroup_info = await tiktok_crawler.get_adgroup(
        advertiser_id=ad["advertiser_id"], adgroup_ids=[ad["adgroup_id"]]
    )
    campaign_info = await tiktok_crawler.get_campaign(
        advertiser_id=ad["advertiser_id"], campaign_ids=[ad["campaign_id"]]
    )

    return {
        "ad": ad,
        "adgroup": (
            adgroup_info["data"]["list"][0]
            if adgroup_info.get("data", {}).get("list")
            else {}
        ),
        "campaign": (
            campaign_info["data"]["list"][0]
            if campaign_info.get("data", {}).get("list")
            else {}
        ),
    }


async def process_single_advertiser(
    tiktok_crawler: TiktokAdCrawler,
    advertiser_id: str,
    start_date: str,
    end_date: str,
    metadata: Dict,
) -> List[Dict]:
    """
    Process a single advertiser and collect all related data.
    """
    # Get advertiser details
    advertiser_info = await tiktok_crawler.get_advertiser_info(advertiser_id)

    # Get all campaigns for this advertiser
    campaigns = await tiktok_crawler.get_campaign(advertiser_id)

    # Get reports for this advertiser
    reports = await tiktok_crawler.get_integrated_report(
        advertiser_id=advertiser_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Collect detailed information for each ad mentioned in reports
    detailed_data = []
    for report in reports:
        ad_id = report.get("dimensions", {}).get("ad_id")
        if ad_id:
            ad_details = await get_ad_details(tiktok_crawler, ad_id)
            detailed_data.append(
                {
                    "report": report,
                    **ad_details,
                    "advertiser": advertiser_info.get("data", {}).get("list", [{}])[0],
                }
            )

    return detailed_data


async def main():
    access_token = "xxx"
    app_id = "xxx"
    secret = "xxx"

    output_file = "tiktok_detailed_data.jsonl"
    start_date = "2025-03-01"
    end_date = "2025-03-31"

    metadata = {
        "ingest": {
            "source": "crawling:tiktok_ad_detailed",
            "destination": {
                "type": "elasticsearch",
                "index": "a_quang_nguyen_tiktok_ad_detailed",
            },
            "vada_client_id": "a_quang_nguyen",
            "type": "tiktok_ad_detailed",
        }
    }

    tiktok_crawler = TiktokAdCrawler(access_token, app_id, secret)

    try:
        # Get all advertisers
        advertisers = await tiktok_crawler.get_advertiser()
        if (
            not advertisers
            or "data" not in advertisers
            or "list" not in advertisers["data"]
        ):
            print("No advertisers found")
            return

        # For testing, just use the last advertiser
        test_advertiser = advertisers["data"]["list"][-1]
        advertiser_id = test_advertiser["advertiser_id"]

        print(f"Processing advertiser {advertiser_id}")

        # Process the test advertiser
        detailed_data = await process_single_advertiser(
            tiktok_crawler, advertiser_id, start_date, end_date, metadata
        )

        # Add metadata and write to JSONL
        enriched_data = append_metadata(detailed_data, metadata)
        write_to_jsonl(output_file, enriched_data)

        print(f"Written {len(detailed_data)} detailed records to {output_file}")

    finally:
        await tiktok_crawler.session.close()


if __name__ == "__main__":
    asyncio.run(main())
