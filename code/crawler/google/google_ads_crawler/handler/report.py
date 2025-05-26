import logging
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram  # type: ignore

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from dependency.profile import log_execution_time
from dependency.google_ad_client import get_google_ads_client
from .metric import METRIC_FIELDS
from .query import build_report_query
from .account import get_all_account_hierarchies, get_non_manager_accounts
from .persist import post_processing


google_ad_crawl = Counter(
    "google_ad_crawl",
    "Total number of crawls",
    ["account_email", "vada_uid"],
)
google_ad_crawl_success = Counter(
    "google_ad_crawl_success",
    "Total number of successful crawls",
    ["account_email", "vada_uid"],
)
google_ad_crawl_latency = Histogram(
    "google_ad_crawl_latency_seconds",
    "Latency of Google Ad crawls in seconds",
    ["account_email", "vada_uid"],
)


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
    """Process reports for a single Google Ads account."""
    logging.info(
        f"│   ├── Getting reports for: {account['descriptive_name']} "
        f"({account['customer_id']})"
    )

    try:
        query = build_report_query(start_date, end_date)
        response = await asyncio.to_thread(
            googleads_service.search,
            customer_id=str(account["customer_id"]),
            query=query,
        )

        account_results = []
        for row in response:
            metrics = get_metrics_from_row(row.metrics)

            report_data = {
                # Segment fields
                "date": row.segments.date,
                # Customer fields
                "customer_id": row.customer.id,
                "customer_descriptive_name": row.customer.descriptive_name,
                "customer_resource_name": row.customer.resource_name,
                # Campaign fields
                "campaign": {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "resource_name": row.campaign.resource_name,
                    "status": row.campaign.status.name,
                    "serving_status": row.campaign.serving_status.name,
                    "payment_mode": row.campaign.payment_mode.name,
                    "optimization_score": float(row.campaign.optimization_score),
                    "advertising_channel_type": row.campaign.advertising_channel_type.name,
                    "advertising_channel_sub_type": row.campaign.advertising_channel_sub_type.name,
                    "bidding_strategy_type": row.campaign.bidding_strategy_type.name,
                    "labels": [label.name for label in row.campaign.labels],
                    "start_date": row.campaign.start_date,
                    "end_date": row.campaign.end_date,
                },
                # Ad group fields
                "ad_group": {
                    "id": row.ad_group.id,
                    "name": row.ad_group.name,
                    "resource_name": row.ad_group.resource_name,
                    "status": row.ad_group.status.name,
                    "primary_status": row.ad_group.primary_status.name,
                    "primary_status_reasons": [
                        reason.name for reason in row.ad_group.primary_status_reasons
                    ],
                    "type": row.ad_group.type_.name,
                    "labels": [label.name for label in row.ad_group.labels],
                    "base_ad_group": row.ad_group.base_ad_group,
                    "campaign": row.ad_group.campaign,
                },
                # Ad group ad fields
                "ad_group_ad": {
                    "ad_id": row.ad_group_ad.ad.id,
                    "ad_name": row.ad_group_ad.ad.name,
                    "ad_resource_name": row.ad_group_ad.ad.resource_name,
                    "added_by_google_ads": row.ad_group_ad.ad.added_by_google_ads,
                    "resource_name": row.ad_group_ad.resource_name,
                    "status": row.ad_group_ad.status.name,
                    "strength": row.ad_group_ad.ad_strength.name,
                    "labels": [label.name for label in row.ad_group_ad.labels],
                },
                # Metrics
                **metrics,
            }
            account_results.append(report_data)

        record_count = len(account_results)
        logging.info(f"│   │   └── Found {record_count} records")
        return account_results

    except Exception as search_error:
        if "CUSTOMER_NOT_ENABLED" in str(search_error):
            logging.warning(f"│   ⚠️  Account {account['customer_id']} is not enabled")
        elif "PERMISSION_DENIED" in str(search_error):
            logging.warning(
                f"│   ⚠️  No permission to access account {account['customer_id']}"
            )
        else:
            logging.error(
                f"│   ⚠️  Error getting reports for {account['descriptive_name']} "
                f"({account['customer_id']}): {str(search_error)}",
                exc_info=True,
            )
        return []


@log_execution_time
async def get_reports(
    ga_client: GoogleAdsClient,
    start_date: str = "",
    end_date: str = "",
    customer_ads_accounts: List = [],
) -> List[Dict]:
    """Fetch Google Ads reports for all accounts through hierarchy.

    Args:
        ga_client: Google Ads API client
        start_date: Start date for report data
        end_date: End date for report data
        customer_ads_accounts: Flatten list of customer accounts (non manager)

    Returns:
        List of campaign/ad group performance data with metrics
    """
    logging.info("=== Getting Performance Reports ===")
    results = []
    total_processed = 0

    for account in customer_ads_accounts:
        # Set login_customer_id to account for all queries
        ga_client.login_customer_id = str(account["customer_id"])
        googleads_service = ga_client.get_service("GoogleAdsService")

        account_results = await process_single_account_report(
            googleads_service, account, start_date, end_date
        )
        if account_results:
            results.extend(account_results)
            total_processed += len(account_results)

    logging.info(
        f"└── Completed processing {total_processed} records from {len({r["customer_id"] for r in results})} accounts"
    )
    logging.info("=== Completed Performance Reports ===")

    return results


async def fetch_google_reports(
    refresh_token: str,
    persist: bool,
    start_date: str = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d"),
    end_date: str = datetime.now().date().strftime("%Y-%m-%d"),
    index_name: str = "",
    account_email: str = "na",
    vada_uid: str = "na",
):
    # Validate date formats
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_dt > end_dt:
            raise ValueError("start_date cannot be later than end_date")

    # Prometheus metrics
    start_time = datetime.now()
    google_ad_crawl.labels(account_email=account_email, vada_uid=vada_uid).inc()

    # Initialize client
    ga_client = await get_google_ads_client(refresh_token)
    logging.info(f"Fetching reports from {start_date} to {end_date}")

    # Get account hierarchies
    hierarchies = await get_all_account_hierarchies(ga_client)
    customer_ads_accounts = get_non_manager_accounts(hierarchies)

    # Get report data
    ad_reports = await get_reports(
        ga_client, start_date, end_date, customer_ads_accounts
    )

    # Process and send reports to insert service if any ads
    if ad_reports:
        if persist and index_name:
            insert_response = await post_processing(ad_reports, index_name)
            logging.info(
                "Sending to Insert service. Index: %s. Response: %s",
                index_name,
                insert_response,
            )

    # Build response with hierarchy information
    response_data = {
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "account": {
            "hierarchy": hierarchies,
            "customer_ads_accounts": customer_ads_accounts,
        },
        "report": {
            "total_campaigns": len(set(r["campaign"]["id"] for r in ad_reports)),
            "total_ad_groups": len(set(r["ad_group"]["id"] for r in ad_reports)),
            "total_ads": len(set(r["ad_group_ad"]["ad_id"] for r in ad_reports)),
            "total_reports": len(ad_reports),
            "reports": ad_reports,
        },
    }
    logging.info(f"Returning {len(ad_reports)} reports")

    # Prometheus metrics
    google_ad_crawl_success.labels(account_email=account_email, vada_uid=vada_uid).inc()
    latency = (datetime.now() - start_time).total_seconds()
    google_ad_crawl_latency.labels(
        account_email=account_email, vada_uid=vada_uid
    ).observe(latency)

    return response_data
