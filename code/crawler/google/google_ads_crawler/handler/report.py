import logging
from typing import Dict, List

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from dependency.profile import log_execution_time
from .account import get_all_account_hierarchies
from .metric import METRIC_FIELDS
from .query import build_report_query


def get_metrics_from_row(metrics_obj) -> Dict:
    """Extract metrics from a Google Ads metrics object using global field definitions"""
    metrics = {}

    for metric_name, field_info in METRIC_FIELDS.items():
        field_name = field_info["field"]
        field_type = field_info["type"]
        value = getattr(metrics_obj, field_name, 0)

        if not value:
            metrics[metric_name] = 0
            continue

        # Handle numeric types
        if field_type == "money":
            metrics[metric_name] = float(value) / 1_000_000
        elif field_type == "integer":
            metrics[metric_name] = int(value)
        elif field_type in ["rate", "share", "float"]:
            metrics[metric_name] = float(value)
        else:
            # Default case
            metrics[metric_name] = value

    return metrics


async def process_single_account_report(
    googleads_service, account: Dict, start_date: str, end_date: str
) -> List[Dict]:
    """Process reports for a single Google Ads account.

    Args:
        googleads_service: Google Ads API service client
        query: Query string to execute
        account: Dictionary containing account information

    Returns:
        List[Dict]: List of processed report data
    """
    logging.info(
        f"│   ├── Getting reports for: {account['descriptive_name']} "
        f"({account['customer_id']})"
    )

    try:
        query = build_report_query(start_date, end_date)
        response = googleads_service.search(
            customer_id=str(account["customer_id"]), query=query
        )

        account_results = []
        for row in response:
            metrics = get_metrics_from_row(row.metrics)

            # Build report data structure
            report_data = {
                # Date info
                "date": row.segments.date,
                # Account hierarchy info
                "customer_id": account["customer_id"],
                "customer_name": account["descriptive_name"],
                # Campaign data
                "campaign": {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "resource_name": row.campaign.resource_name,
                    "status": row.campaign.status.name,
                    "serving_status": row.campaign.serving_status.name,
                    "payment_mode": row.campaign.payment_mode.name,
                    "optimization_score": float(row.campaign.optimization_score),
                    "start_date": row.campaign.start_date,
                    "end_date": row.campaign.end_date,
                },
                # Ad group data
                "ad_group": {
                    "id": row.ad_group.id,
                    "name": row.ad_group.name,
                    "resource_name": row.ad_group.resource_name,
                    "status": row.ad_group.status.name,
                    "type": row.ad_group.type_.name,
                    "base_ad_group": row.ad_group.base_ad_group,
                    "campaign": row.ad_group.campaign,
                },
                # Ad data
                "ad": {
                    "id": row.ad_group_ad.ad.id,
                    "name": row.ad_group_ad.ad.name,
                    "resource_name": row.ad_group_ad.ad.resource_name,
                    "ad_group_ad_resource_name": row.ad_group_ad.resource_name,
                    "status": row.ad_group_ad.status.name,
                },
                **metrics,
            }
            account_results.append(report_data)

        record_count = len(account_results)
        logging.info(f"│   │   └── Found {record_count} records")
        return account_results

    except Exception as e:
        logging.error(
            f"│   ⚠️  Error getting reports for {account['descriptive_name']} "
            f"({account['customer_id']}): {str(e)}",
            exc_info=True,
        )
        return []


async def process_account_hierarchy(
    googleads_service,
    account: Dict,
    start_date: str,
    end_date: str,
    parent: Dict | None = None,
) -> List[Dict]:
    """Process reports for an account and all its children recursively.

    Args:
        googleads_service: Google Ads API service client
        account: Account to process
        start_date: Start date for report data
        end_date: End date for report data
        parent: Optional parent manager account

    Returns:
        List[Dict]: Combined list of all report data
    """
    results = []

    # Process non-manager account
    if not account.get("manager", False):
        account_results = await process_single_account_report(
            googleads_service, account, start_date, end_date
        )
        if account_results:
            # Add parent manager info if available
            for result in account_results:
                if parent:
                    result["manager_id"] = parent["customer_id"]
                    result["manager_name"] = parent["descriptive_name"]
            results.extend(account_results)
        return results

    # Process manager account's children
    logging.info(
        f"├── Processing manager account: {account['descriptive_name']} "
        f"({account['customer_id']})"
    )

    if not account.get("children"):
        logging.info("│   └── No child accounts found")
        return results

    total_processed = 0
    for child in account["children"]:
        # Recursively process each child (which might be another manager)
        child_results = await process_account_hierarchy(
            googleads_service, child, start_date, end_date, account
        )
        results.extend(child_results)
        total_processed += len(child_results)

    if total_processed:
        logging.info(
            f"│   └── Total records for {account['descriptive_name']}: {total_processed}"
        )

    return results


@log_execution_time
async def get_reports(
    ga_client: GoogleAdsClient,
    start_date: str,
    end_date: str,
    hierarchies: Dict | None = None,
) -> List[Dict]:
    """Fetch Google Ads reports for all accounts through hierarchy.

    Args:
        ga_client: Google Ads API client
        start_date: Start date for report data
        end_date: End date for report data
        hierarchies: Account hierarchy data from get_all_account_hierarchies

    Returns:
        List of campaign/ad group performance data with metrics
    """
    logging.info("=== Getting Performance Reports ===")
    googleads_service = ga_client.get_service("GoogleAdsService")
    results = []
    total_processed = 0

    # Get hierarchies if not provided
    if not hierarchies:
        hierarchies = await get_all_account_hierarchies(ga_client)

    # Process each root account recursively
    for root in hierarchies:
        root_results = await process_account_hierarchy(
            googleads_service, root, start_date, end_date
        )
        results.extend(root_results)
        total_processed += len(root_results)

    # Count unique accounts processed
    unique_accounts = len({r["customer_id"] for r in results})

    logging.info(
        f"└── Completed processing {total_processed} records from {unique_accounts} accounts"
    )
    logging.info("=== Completed Performance Reports ===")

    return results
