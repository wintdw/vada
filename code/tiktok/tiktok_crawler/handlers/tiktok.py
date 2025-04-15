import json
import hashlib

from typing import Dict


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


def save_report(data, filename):
    with open(filename, "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")


def generate_doc_id(data: Dict) -> str:
    serialized_data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def enrich_report(report: Dict, index_name: str, doc_id: str) -> Dict:
    metadata = {
        "_vada": {
            "ingest": {
                "destination": {"type": "elasticsearch", "index": index_name},
                "vada_client_id": "a_quang_nguyen",
                "doc_id": doc_id,
            }
        }
    }
    return report | metadata
