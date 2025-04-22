import logging
from typing import Dict, List

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from dependency.profile import log_execution_time
from .customer import get_manager_accounts

# Define all metric fields used in reports
METRIC_FIELDS = {
    # Impression & Position metrics
    "impressions": {"field": "impressions", "type": "integer"},
    "absolute_top_impression_percentage": {
        "field": "absolute_top_impression_percentage",
        "type": "rate",
    },
    "top_impression_percentage": {"field": "top_impression_percentage", "type": "rate"},
    # Cost metrics
    "cost": {"field": "cost_micros", "type": "money"},
    "average_cost": {"field": "average_cost", "type": "money"},
    "average_cpc": {"field": "average_cpc", "type": "money"},
    "average_cpe": {"field": "average_cpe", "type": "money"},
    "average_cpm": {"field": "average_cpm", "type": "money"},
    "average_cpv": {"field": "average_cpv", "type": "money"},
    # Click & Engagement metrics
    "clicks": {"field": "clicks", "type": "integer"},
    "ctr": {"field": "ctr", "type": "rate"},
    "engagements": {"field": "engagements", "type": "integer"},
    "engagement_rate": {"field": "engagement_rate", "type": "rate"},
    "interaction_rate": {"field": "interaction_rate", "type": "rate"},
    "interactions": {"field": "interactions", "type": "integer"},
    "interaction_event_types": {"field": "interaction_event_types", "type": "string"},
    # Conversion metrics
    "conversions": {"field": "conversions", "type": "float"},
    "conversions_value": {"field": "conversions_value", "type": "float"},
    "cost_per_conversion": {"field": "cost_per_conversion", "type": "money"},
    "value_per_conversion": {"field": "value_per_conversion", "type": "float"},
    "conversions_from_interactions_rate": {
        "field": "conversions_from_interactions_rate",
        "type": "rate",
    },
    "conversions_by_conversion_date": {
        "field": "conversions_by_conversion_date",
        "type": "float",
    },
    "conversions_value_by_conversion_date": {
        "field": "conversions_value_by_conversion_date",
        "type": "float",
    },
    "conversions_value_per_cost": {
        "field": "conversions_value_per_cost",
        "type": "float",
    },
    "conversions_from_interactions_value_per_interaction": {
        "field": "conversions_from_interactions_value_per_interaction",
        "type": "float",
    },
    # All conversion metrics
    "all_conversions": {"field": "all_conversions", "type": "float"},
    "all_conversions_value": {"field": "all_conversions_value", "type": "float"},
    "cost_per_all_conversions": {"field": "cost_per_all_conversions", "type": "money"},
    "value_per_all_conversions": {
        "field": "value_per_all_conversions",
        "type": "float",
    },
    "all_conversions_by_conversion_date": {
        "field": "all_conversions_by_conversion_date",
        "type": "float",
    },
    "all_conversions_value_by_conversion_date": {
        "field": "all_conversions_value_by_conversion_date",
        "type": "float",
    },
    "all_conversions_value_per_cost": {
        "field": "all_conversions_value_per_cost",
        "type": "float",
    },
    "all_conversions_from_interactions_rate": {
        "field": "all_conversions_from_interactions_rate",
        "type": "rate",
    },
    "all_conversions_from_interactions_value_per_interaction": {
        "field": "all_conversions_from_interactions_value_per_interaction",
        "type": "float",
    },
    # Cross-device metrics
    "cross_device_conversions": {"field": "cross_device_conversions", "type": "float"},
    "cross_device_conversions_value_micros": {
        "field": "cross_device_conversions_value_micros",
        "type": "money",
    },
    # Current model metrics
    "current_model_attributed_conversions": {
        "field": "current_model_attributed_conversions",
        "type": "float",
    },
    "current_model_attributed_conversions_value": {
        "field": "current_model_attributed_conversions_value",
        "type": "float",
    },
    "cost_per_current_model_attributed_conversion": {
        "field": "cost_per_current_model_attributed_conversion",
        "type": "money",
    },
    "value_per_current_model_attributed_conversion": {
        "field": "value_per_current_model_attributed_conversion",
        "type": "float",
    },
    "current_model_attributed_conversions_from_interactions_rate": {
        "field": "current_model_attributed_conversions_from_interactions_rate",
        "type": "rate",
    },
    "current_model_attributed_conversions_from_interactions_value_per_interaction": {
        "field": "current_model_attributed_conversions_from_interactions_value_per_interaction",
        "type": "float",
    },
    "current_model_attributed_conversions_value_per_cost": {
        "field": "current_model_attributed_conversions_value_per_cost",
        "type": "float",
    },
    # Video metrics
    "video_views": {"field": "video_views", "type": "integer"},
    "video_view_rate": {"field": "video_view_rate", "type": "rate"},
    "video_quartile_p25_rate": {"field": "video_quartile_p25_rate", "type": "rate"},
    "video_quartile_p50_rate": {"field": "video_quartile_p50_rate", "type": "rate"},
    "video_quartile_p75_rate": {"field": "video_quartile_p75_rate", "type": "rate"},
    "video_quartile_p100_rate": {"field": "video_quartile_p100_rate", "type": "rate"},
    # Active View metrics
    "active_view_impressions": {"field": "active_view_impressions", "type": "integer"},
    "active_view_cpm": {"field": "active_view_cpm", "type": "money"},
    "active_view_ctr": {"field": "active_view_ctr", "type": "rate"},
    "active_view_viewability": {"field": "active_view_viewability", "type": "rate"},
    "active_view_measurable_impressions": {
        "field": "active_view_measurable_impressions",
        "type": "integer",
    },
    "active_view_measurable_cost_micros": {
        "field": "active_view_measurable_cost_micros",
        "type": "money",
    },
    "active_view_measurability": {"field": "active_view_measurability", "type": "rate"},
    # Gmail specific metrics
    "gmail_forwards": {"field": "gmail_forwards", "type": "integer"},
    "gmail_saves": {"field": "gmail_saves", "type": "integer"},
    "gmail_secondary_clicks": {"field": "gmail_secondary_clicks", "type": "integer"},
    # Phone metrics
    "phone_calls": {"field": "phone_calls", "type": "integer"},
    "phone_impressions": {"field": "phone_impressions", "type": "integer"},
    "phone_through_rate": {"field": "phone_through_rate", "type": "rate"},
    # Website metrics
    "bounce_rate": {"field": "bounce_rate", "type": "rate"},
    "average_page_views": {"field": "average_page_views", "type": "float"},
    "average_time_on_site": {"field": "average_time_on_site", "type": "float"},
    "percent_new_visitors": {"field": "percent_new_visitors", "type": "rate"},
    # Revenue & profit metrics
    "revenue_micros": {"field": "revenue_micros", "type": "money"},
    "cost_of_goods_sold_micros": {
        "field": "cost_of_goods_sold_micros",
        "type": "money",
    },
    "gross_profit_micros": {"field": "gross_profit_micros", "type": "money"},
    "gross_profit_margin": {"field": "gross_profit_margin", "type": "rate"},
    # Customer metrics
    "average_order_value_micros": {
        "field": "average_order_value_micros",
        "type": "money",
    },
    "average_cart_size": {"field": "average_cart_size", "type": "float"},
    "orders": {"field": "orders", "type": "integer"},
    "units_sold": {"field": "units_sold", "type": "integer"},
    # Cross-sell metrics
    "cross_sell_cost_of_goods_sold_micros": {
        "field": "cross_sell_cost_of_goods_sold_micros",
        "type": "money",
    },
    "cross_sell_gross_profit_micros": {
        "field": "cross_sell_gross_profit_micros",
        "type": "money",
    },
    "cross_sell_revenue_micros": {
        "field": "cross_sell_revenue_micros",
        "type": "money",
    },
    "cross_sell_units_sold": {"field": "cross_sell_units_sold", "type": "integer"},
    # Lead metrics
    "lead_cost_of_goods_sold_micros": {
        "field": "lead_cost_of_goods_sold_micros",
        "type": "money",
    },
    "lead_gross_profit_micros": {"field": "lead_gross_profit_micros", "type": "money"},
    "lead_revenue_micros": {"field": "lead_revenue_micros", "type": "money"},
    "lead_units_sold": {"field": "lead_units_sold", "type": "integer"},
    # Customer lifetime value metrics
    "new_customer_lifetime_value": {
        "field": "new_customer_lifetime_value",
        "type": "float",
    },
    "all_new_customer_lifetime_value": {
        "field": "all_new_customer_lifetime_value",
        "type": "float",
    },
    # View-through conversions
    "view_through_conversions": {"field": "view_through_conversions", "type": "float"},
}


def build_report_query(start_date: str, end_date: str) -> str:
    """Build query for ad, campaign and ad group performance data"""
    metric_fields = [
        f"metrics.{field_info['field']}" for field_info in METRIC_FIELDS.values()
    ]

    return """
        SELECT
            segments.date,
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.status,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.status,
            {metrics}
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status != 'REMOVED'
        AND ad_group.status != 'REMOVED'
        AND ad_group_ad.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """.format(
        start_date=start_date,
        end_date=end_date,
        metrics=",\n            ".join(metric_fields),
    )


def get_metrics_from_row(metrics_obj) -> dict:
    """Extract metrics from a Google Ads metrics object using global field definitions"""
    metrics = {}

    for metric_name, field_info in METRIC_FIELDS.items():
        field_name = field_info["field"]
        field_type = field_info["type"]
        value = getattr(metrics_obj, field_name, 0)

        if not value:
            metrics[metric_name] = 0
            continue

        if field_type == "money":
            metrics[metric_name] = float(value) / 1_000_000
        elif field_type == "integer":
            metrics[metric_name] = int(value)
        elif field_type in ["rate", "share"]:
            metrics[metric_name] = float(value)
        else:
            metrics[metric_name] = float(value)

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

                child_results = []  # Track results for this child only

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

                    ad_data = {
                        "id": row.ad_group_ad.ad.id,
                        "name": row.ad_group_ad.ad.name,
                        "status": row.ad_group_ad.status.name,
                    }

                    child_results.append(
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
                            "ad": ad_data,
                            # Flat metrics
                            **metrics,
                        }
                    )

                results.extend(child_results)  # Add child results to main results
                if child_results:
                    logging.info(f"│   │   └── Found {len(child_results)} records")

            except Exception as e:
                logging.error(
                    f"│   ⚠️  Error getting reports for {child['name']}: {str(e)}",
                    exc_info=True,
                )
                continue

    logging.info(f"└── Completed processing with {len(results)} total records")
    logging.info("=== Completed Performance Reports ===")

    return results
