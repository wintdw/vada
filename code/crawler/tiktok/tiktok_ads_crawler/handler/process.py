from datetime import datetime
from typing import Dict


def standardize_doc(doc: Dict, type: str) -> Dict:
    """
    Standardizes the report dictionary by ensuring required fields are valid.

    Ensure total_onsite_shopping_value is a number; set to 0 if not.
    Remove item_list field if present.
    """

    # total_onsite_shopping_value
    if type == "ad":
        total_onsite_shopping_value = doc.get("total_onsite_shopping_value", "")
        if not isinstance(total_onsite_shopping_value, (int, float)):
            doc["total_onsite_shopping_value"] = 0
    elif type == "gmv":
        # Remove item_list field if present
        doc.pop("item_list", None)

    return doc


def enrich_doc(doc: Dict, type: str) -> Dict:
    """
    Enrich a report with vada ingest metadata and, if applicable, company-specific metadata.

    Args:
        doc (dict): The original or already enriched report
        type (str): "ad" or "gmv"

    Returns:
        dict: Enriched report
    """
    if type == "gmv":
        doc_id = f"{doc.get('advertiser_id')}_{doc.get('campaign_id')}"
    else:
        timestamp = int(
            datetime.strptime(doc["stat_time_day"], "%Y-%m-%d %H:%M:%S").timestamp()
        )
        doc_id = f"{doc['ad_id']}_{timestamp}"

    metadata = {
        "_vada": {
            "ingest": {
                "doc_id": doc_id,
            }
        }
    }
    enriched = doc | metadata

    # Company-specific enrichment rules
    company_enrichers = {
        "ANCHI GROUP VIET NAM JOINT STOCK COMPANY": enrich_anchi_metadata,
        # Add more company-specific enrichers here as needed
    }

    advertiser = enriched.get("advertiser", {})
    company = advertiser.get("company", "")

    if company in company_enrichers:
        enriched = company_enrichers[company](enriched)

    return enriched


def enrich_anchi_metadata(enriched_report: Dict) -> Dict:
    """
    Enrich report with vada metadata for ANCHI GROUP VIET NAM JOINT STOCK COMPANY.
    """
    advertiser = enriched_report.get("advertiser", {})
    advertiser_name = advertiser.get("name", "")

    if not advertiser_name or "-" not in advertiser_name:
        return enriched_report

    try:
        parts = advertiser_name.split("-")
        if len(parts) >= 4:
            ma_du_an = parts[0]
            kenh_quang_cao = parts[1]
            marketer_id = parts[2]
            sub_account_name = parts[3]

            vada_metadata = {
                "vada": {
                    "ma_du_an": ma_du_an,
                    "kenh_quang_cao": kenh_quang_cao,
                    "marketer_id": marketer_id,
                    "sub_account_name": sub_account_name,
                }
            }
            return enriched_report | vada_metadata
        else:
            return enriched_report
    except Exception:
        return enriched_report
