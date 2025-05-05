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
    metric_fields = [
        f"metrics.{field_info['field']}" for field_info in METRIC_FIELDS.values()
    ]

    query = """
        SELECT
            segments.date,
            customer.id,
            customer.descriptive_name,
            customer.resource_name,
            campaign.id,
            campaign.name,
            campaign.resource_name,
            campaign.status,
            campaign.serving_status,
            campaign.payment_mode,
            campaign.optimization_score,
            campaign.start_date,
            campaign.end_date,
            ad_group.id,
            ad_group.name,
            ad_group.resource_name,
            ad_group.status,
            ad_group.type,
            ad_group.base_ad_group,
            ad_group.campaign,
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.ad.resource_name,
            ad_group_ad.resource_name,
            ad_group_ad.status,
            {metrics}
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    """.format(
        start_date=start_date,
        end_date=end_date,
        metrics=",\n            ".join(metric_fields),
    )

    # logging.debug(f"Generated query: {query}")
    return query
