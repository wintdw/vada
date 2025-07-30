import json


def save_report(data, filename):
    with open(filename, "a", encoding="utf-8") as f:  # Changed "a" to "w"
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")


def construct_detailed_report(
    report: dict,
    advertiser_info: dict,
    campaign_info: dict,
    adgroup_info: dict,
    ad_info: dict,
) -> dict:
    """
    Enhance a report with nested dictionaries for advertiser, campaign, ad group and ad.

    Args:
        report (dict): The original report data
        advertiser_info (dict): Complete advertiser information
        campaign_info (dict): Complete campaign information
        adgroup_info (dict): Complete ad group information
        ad_info (dict): Complete ad information

    Returns:
        dict: Enhanced report with nested entity information
    """
    enhanced_report = report.copy()

    # Create nested dictionaries for each entity
    enhanced_report["advertiser"] = advertiser_info
    enhanced_report["campaign"] = campaign_info
    enhanced_report["adgroup"] = adgroup_info
    enhanced_report["ad"] = ad_info

    return enhanced_report


def enrich_report(report: dict, index_name: str, doc_id: str) -> dict:
    """
    Enrich a report with vada ingest metadata and, if applicable, company-specific metadata.

    Args:
        report (dict): The original or already enriched report
        index_name (str): Elasticsearch index name
        doc_id (str): Document ID

    Returns:
        dict: Enriched report
    """
    # Base vada ingest metadata
    metadata = {
        "_vada": {
            "ingest": {
                "destination": {"type": "elasticsearch", "index": index_name},
                "doc_id": doc_id,
            }
        }
    }
    enriched = report | metadata

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


def enrich_anchi_metadata(enriched_report: dict) -> dict:
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
