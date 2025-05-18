import aiohttp  # type: ignore
from typing import Dict, List

from model.setting import settings
from model.index_mappings import index_mappings_data


def add_insert_metadata(reports: List, index_name: str) -> Dict:
    return {"meta": {"index_name": index_name}, "data": reports}


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


async def send_to_insert_service(data: Dict, insert_service_baseurl: str) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{insert_service_baseurl}/json",
            json=data,
            headers={"Content-Type": "application/json"},
        ) as response:
            return {"status": response.status, "detail": await response.text()}


async def create_crm_mappings(
    index_name: str, vada_uid: str, account_email: str
) -> Dict:
    """Copy CRM mappings from the mappings service
    Args:
        index_name: Name of the index to copy mappings for
        vada_uid: Vada user ID
        account_email: Account email of the Google account - for friendly name
    """

    async def create_crm_mappings_handler(
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mappings: Dict,
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ) -> Dict:
        url = f"{settings.MAPPINGS_BASE_URL}/crm/mappings"

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
            "mappings": mappings,
            "id_field": id_field,
            "agg_field": agg_field,
            "time_field": time_field,
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=payload) as response:
                return await response.json()

    response = await create_crm_mappings_handler(
        user_id=vada_uid,
        index_name=index_name,
        index_friendly_name=f"Google Ads {account_email}",
        mappings=index_mappings_data["mappings"],
        id_field="customer_id",
        agg_field="customer_id",
        time_field="date",
    )
    return response


### The main function to process and send reports
async def post_processing(raw_reports: List[Dict], index_name: str) -> Dict:
    """Produce data to insert service
    then use mapping to create CRM index

    Args:
        raw_reports: List of report data to be processed and sent

    Returns:
        Dict: Response from insert service
    """

    # Enrich each report with metadata
    enriched_reports = []
    for report in raw_reports:
        # Create unique doc ID using ad.id + ad_group.id + campaign.id + date
        doc_id = ".".join(
            [
                str(report.get("customer_id", "")),
                str(report.get("campaign", {}).get("id", "")),
                str(report.get("ad_group", {}).get("id", "")),
                str(report.get("ad_group_ad", {}).get("ad_id", "")),
                str(report.get("date", "")),
            ]
        )
        enriched_report = enrich_report(report, index_name, doc_id)
        enriched_reports.append(enriched_report)

    # Add insert metadata wrapper
    enriched_report_data = add_insert_metadata(enriched_reports, index_name)

    # Send to insert service
    response = await send_to_insert_service(
        enriched_report_data, settings.INSERT_SERVICE_BASEURL
    )

    return response
