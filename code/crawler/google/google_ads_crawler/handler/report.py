import logging
from typing import Dict, List, Optional

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from dependency.profile import log_execution_time
from .account import get_manager_accounts
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


@log_execution_time
async def get_reports(
    ga_client: GoogleAdsClient,
    start_date: str,
    end_date: str,
    manager_accounts: Optional[List[Dict]] = None,
) -> List[Dict]:
    """Fetch Google Ads reports for all non-manager accounts through hierarchy.

    Args:
        ga_client: Google Ads API client
        start_date: Start date for report data
        end_date: End date for report data
        manager_accounts: Optional list of manager accounts with their children (for caching)

    Returns:
        List of campaign/ad group performance data with metrics
    """
    logging.info("=== Getting Performance Reports ===")
    query = build_report_query(start_date, end_date)

    googleads_service = ga_client.get_service("GoogleAdsService")
    results = []

    # Get manager accounts if not provided
    if manager_accounts is None:
        manager_accounts = await get_manager_accounts(ga_client)

    for manager in manager_accounts:
        manager_total = 0  # Track total records for this manager
        logging.info(
            f"├── Processing manager: {manager['descriptive_name']} ({manager['customer_id']})"
        )

        # Skip managers without children
        if not manager["child_accounts"]:
            logging.info(f"│   └── Skipping manager with no child accounts")
            continue

        # Process each non-manager child account
        for child in manager["child_accounts"]:
            if child["manager"]:
                continue

            try:
                logging.info(
                    f"│   ├── Getting reports for child: {child['descriptive_name']}"
                )
                response = googleads_service.search(
                    customer_id=child["customer_id"], query=query
                )

                child_results = []  # Track results for this child only

                for row in response:
                    # Get metrics dynamically
                    metrics = get_metrics_from_row(row.metrics)

                    # Structured campaign and ad group data
                    campaign_data = {
                        "id": row.campaign.id,
                        "name": row.campaign.name,
                        "status": row.campaign.status.name,
                    }

                    ad_group_data = {
                        "id": row.ad_group.id,
                        "name": row.ad_group.name,
                        "status": row.ad_group.status.name,
                    }

                    ad_data = {
                        "id": row.ad_group_ad.ad.id,
                        "name": row.ad_group_ad.ad.name,
                        "status": row.ad_group_ad.status.name,
                    }

                    child_results.append(
                        {
                            # Account info
                            "customer_id": child["customer_id"],
                            "customer_name": child["descriptive_name"],
                            "manager_id": manager["customer_id"],
                            "manager_name": manager["descriptive_name"],
                            # Date info
                            "date": row.segments.date,
                            # Structured data
                            "campaign": campaign_data,
                            "ad_group": ad_group_data,
                            "ad": ad_data,
                            # Flat metrics
                            **metrics,
                        }
                    )

                results.extend(child_results)  # Add child results to main results
                if child_results:
                    child_count = len(child_results)
                    manager_total += child_count
                    logging.info(f"│   │   └── Found {child_count} records")

            except Exception as e:
                if "CUSTOMER_NOT_ENABLED" in str(e):
                    logging.warning(
                        f"│   ⚠️  Account {child['descriptive_name']} ({child['customer_id']}) is not enabled"
                    )
                elif "PERMISSION_DENIED" in str(e):
                    logging.warning(
                        f"│   ⚠️  No permission to access account {child['descriptive_name']} ({child['customer_id']})"
                    )
                else:
                    logging.error(
                        f"│   ⚠️  Error getting reports for {child['descriptive_name']} ({child['customer_id']}): {str(e)}",
                        exc_info=True,
                    )
                continue

        logging.info(
            f"│   └── Total records for {manager['descriptive_name']}: {manager_total}"
        )

    logging.info(f"└── Completed processing with {len(results)} total records")
    logging.info("=== Completed Performance Reports ===")

    return results
