def build_customer_query(
    customer_id: str, is_manager: bool = False, is_enabled: bool = True
) -> str:
    """Build standardized account query.

    Args:
        customer_id: Account ID to query
        is_manager: Whether to query manager accounts
        is_enabled: If True, query ENABLED accounts. If False, query non-ENABLED accounts

    Returns:
        SQL query string
    """
    return """
        SELECT 
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.auto_tagging_enabled,
            customer.status,
            customer.test_account,
            customer.pay_per_conversion_eligibility_failure_reasons
        FROM customer 
        WHERE customer.id = '{customer_id}'
        AND customer.manager = {is_manager}
        AND customer.status {operator} 'ENABLED'
    """.format(
        customer_id=customer_id,
        is_manager=str(is_manager).upper(),
        operator="=" if is_enabled else "!=",
    )


def build_customer_client_query(manager_id: str, is_enabled: bool = True) -> str:
    """Build standardized account client query.

    Args:
        customer_id: Account ID to query

    Returns:
        SQL query string
    """
    return """
        SELECT 
            customer_client.id,
            customer_client.descriptive_name,
            customer_client.client_customer,
            customer_client.level,
            customer_client.status,
            customer_client.manager,
            customer_client.currency_code,
            customer_client.time_zone
        FROM customer_client
        WHERE customer_client.id != {manager_id}
        AND customer_client.status {operator} 'ENABLED'
    """.format(
        manager_id=manager_id,
        operator="=" if is_enabled else "!=",
    )
