import logging
import aiohttp  # type: ignore
from typing import Dict, List

from model.setting import settings


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


### The main function to process and send reports
async def post_processing(raw_reports: List[Dict], index_name: str) -> Dict:
    """Produce data to insert service in batches of 1000

    Args:
        raw_reports: List of report data to be processed and sent

    Returns:
        Dict: Last response from insert service
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

    batch_size = 1000
    total_reports = len(enriched_reports)
    total_batches = (total_reports + batch_size - 1) // batch_size
    last_response = {}

    for i in range(0, total_reports, batch_size):
        batch = enriched_reports[i : i + batch_size]
        current_batch = i // batch_size + 1

        enriched_report_data = add_insert_metadata(batch, index_name)
        response = await send_to_insert_service(
            enriched_report_data, settings.INSERT_SERVICE_BASEURL
        )
        status = response.get("status", 0)
        if status != 200:
            logging.error(
                f"Batch {current_batch}/{total_batches} failed - Status: {status} - Detail: {response.get('detail', '')}"
            )
        last_response = response

    return last_response
