import logging
from .metric import METRIC_FIELDS


def build_customer_query(where_clause: str | None = None) -> str:
    """Build standardized account query.

    Args:
        customer_id: Optional account ID to query. If provided, adds WHERE customer.id = {id}
        where_clause: Optional additional WHERE clause conditions.
                     Takes precedence over customer_id if both provided.

    Returns:
        SQL query string
    """
    query = """
        SELECT 
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.auto_tagging_enabled,
            customer.status,
            customer.test_account
        FROM customer
        {where_statement}
    """.format(
        where_statement=(f"WHERE {where_clause}" if where_clause else "")
    )

    # logging.debug(f"Generated query: {query}")
    return query


def build_customer_client_query(where_clause: str | None = None) -> str:
    """Build standardized account client query.

    Args:
        where_clause: Optional additional WHERE clause conditions.
                     If None, will select all client accounts.

    Returns:
        SQL query string
    """

    query = """
        SELECT 
            customer_client.id,
            customer_client.descriptive_name,
            customer_client.client_customer,
            customer_client.level,
            customer_client.status,
            customer_client.manager,
            customer_client.currency_code,
            customer_client.time_zone,
            customer_client.test_account
        FROM customer_client
        {where_statement}
    """.format(
        where_statement=f"WHERE {where_clause}" if where_clause else ""
    )

    # logging.debug(f"Generated query: {query}")
    return query


def build_report_query(start_date: str, end_date: str) -> str:
    """Build query for ad, campaign and ad group performance data"""

    segment_fields = ["date"]
    customer_fields = ["id", "descriptive_name", "resource_name"]
    campaign_fields = [
        "id",
        "name",
        "resource_name",
        "status",
        "serving_status",
        "payment_mode",
        "optimization_score",
        "advertising_channel_type",
        "advertising_channel_sub_type",
        "bidding_strategy_type",
        "labels",
        "start_date",
        "end_date",
    ]
    ad_group_fields = [
        "id",
        "name",
        "resource_name",
        "status",
        "primary_status",
        "primary_status_reasons",
        "type",
        "labels",
        "base_ad_group",
        "campaign",
    ]
    ad_group_ad_fields = [
        "ad.id",
        "ad.name",
        "ad.resource_name",
        "ad.added_by_google_ads",
        "resource_name",
        "status",
        "ad_strength",
        "labels",
    ]
    metric_fields = [
        f"metrics.{field_info['field']}" for field_info in METRIC_FIELDS.values()
    ]

    query_fields = (
        [f"segments.{field}" for field in segment_fields]
        + [f"customer.{field}" for field in customer_fields]
        + [f"campaign.{field}" for field in campaign_fields]
        + [f"ad_group.{field}" for field in ad_group_fields]
        + [f"ad_group_ad.{field}" for field in ad_group_ad_fields]
        + metric_fields
    )

    query = """
        SELECT
            {fields}
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    """.format(
        fields=",\n            ".join(query_fields),
        start_date=start_date,
        end_date=end_date,
    )

    # logging.debug(f"Generated query: {query}")
    return query
