import logging

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from dependency.profile import log_execution_time
from .customer import get_manager_accounts


def build_report_query(start_date: str, end_date: str) -> str:
    """Build query for campaign and ad group performance data"""
    return """
        SELECT
            segments.date,
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            metrics.cost_micros,
            metrics.conversions,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.search_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.bounce_rate,
            metrics.average_time_on_site,
            metrics.all_conversions,
            metrics.all_conversions_value,
            metrics.conversions_from_interactions_rate,
            metrics.all_conversions_from_interactions_rate,
            metrics.cost_per_conversion,
            metrics.value_per_conversion,
            metrics.engagements,
            metrics.engagement_rate,
            metrics.video_view_rate,
            metrics.view_through_conversions
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status != 'REMOVED'
        AND ad_group.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """.format(
        start_date=start_date, end_date=end_date
    )


def get_metrics_from_row(metrics_obj) -> dict:
    """Extract all metrics from a Google Ads metrics object dynamically.

    Args:
        metrics_obj: Google Ads metrics object from row

    Returns:
        Dict containing all available metrics with proper value conversion
    """
    metrics = {}

    # Get all available fields from metrics object
    for field in metrics_obj.DESCRIPTOR.fields:
        field_name = field.name
        value = getattr(metrics_obj, field_name, 0)

        # Convert monetary values (ending with _micros)
        if field_name.endswith("_micros"):
            base_name = field_name.replace("_micros", "")
            metrics[base_name] = float(value) / 1_000_000 if value else 0
        # Handle percentage values (rates)
        elif any(field_name.endswith(suffix) for suffix in ["_rate", "_share"]):
            metrics[field_name] = float(value) if value else 0
        # Handle integer metrics
        elif field_name in ["impressions", "clicks", "engagements"]:
            metrics[field_name] = int(value) if value else 0
        # All other metrics as float
        else:
            metrics[field_name] = float(value) if value else 0

    return metrics


@log_execution_time
async def get_reports(client: GoogleAdsClient, start_date, end_date):
    """Fetch Google Ads reports for all non-manager accounts through hierarchy.

    Args:
        client: Google Ads API client
        start_date: Start date for report data
        end_date: End date for report data

    Returns:
        List of campaign/ad group performance data with metrics
    """
    logging.info("=== Getting Performance Reports ===")
    query = build_report_query(
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    ga_service = client.get_service("GoogleAdsService")
    results = []

    # Get manager accounts with their children
    manager_accounts = await get_manager_accounts(client)

    for manager in manager_accounts:
        logging.info(
            f"├── Processing manager: {manager['name']} ({manager['customer_id']})"
        )

        # Skip managers without children
        if not manager["child_accounts"]:
            logging.info(f"│   └── Skipping manager with no child accounts")
            continue

        # Process each non-manager child account
        for child in manager["child_accounts"]:
            if child["is_manager"]:
                continue

            try:
                logging.info(f"│   ├── Getting reports for child: {child['name']}")
                response = ga_service.search(
                    request={"customer_id": child["id"], "query": query}
                )

                for row in response:
                    # Get metrics dynamically
                    metrics = get_metrics_from_row(row.metrics)

                    # Structured campaign and ad group data
                    campaign_data = {
                        "id": row.campaign.id,
                        "name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "channel": row.campaign.advertising_channel_type.name,
                        "bidding": row.campaign.bidding_strategy_type.name,
                    }

                    ad_group_data = {
                        "id": row.ad_group.id,
                        "name": row.ad_group.name,
                        "status": row.ad_group.status.name,
                    }

                    results.append(
                        {
                            # Account info
                            "customer_id": child["id"],
                            "customer_name": child["name"],
                            "manager_id": manager["customer_id"],
                            "manager_name": manager["name"],
                            # Date info
                            "date": row.segments.date,
                            # Structured data
                            "campaign": campaign_data,
                            "ad_group": ad_group_data,
                            # Flat metrics
                            **metrics,
                        }
                    )

                if results:
                    logging.info(f"│   │   └── Found {len(results)} records")

            except Exception as e:
                logging.error(
                    f"│   ⚠️  Error getting reports for {child['name']}: {str(e)}",
                    exc_info=True,
                )
                continue

    logging.info(f"└── Completed processing with {len(results)} total records")
    logging.info("=== Completed Performance Reports ===")

    return results
