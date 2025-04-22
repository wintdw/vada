import logging
from typing import Dict, List, Optional

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from dependency.profile import log_execution_time

# Common keys for account data
ACCOUNT_FIELDS = {
    "id": "customer_id",  # Standardize ID field name
    "name": "name",
    "currency": "currency",
    "timezone": "timezone",
    "status": "status",
    "resource_name": "resource_name",
    "auto_tagging": "auto_tagging",
    "is_test_account": "is_test_account",
    "pay_per_conversion_issues": "pay_per_conversion_issues",
    "metrics": "metrics",
}


def build_account_query(customer_id: str, is_manager: bool = False) -> str:
    """Build standardized account query.

    Args:
        customer_id: Account ID to query
        is_manager: Whether to query manager accounts

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
    """.format(
        customer_id=customer_id, is_manager=str(is_manager).upper()
    )


@log_execution_time
async def get_metrics_for_account(
    ga_service: GoogleAdsClient, customer_id: str
) -> Dict[str, float]:
    """Get metrics for a specific account.

    Args:
        ga_service: Google Ads service client
        customer_id: Account ID to get metrics for

    Returns:
        Dict containing account metrics (cost, impressions, clicks, etc.)
    """
    logging.info(f"└── Getting metrics for account {customer_id}")
    try:
        metrics_response = ga_service.search(
            request={
                "customer_id": str(customer_id),
                "query": """
                SELECT
                    metrics.cost_micros,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.average_cpc
                FROM customer
                WHERE customer.id = '{customer_id}'
            """.format(
                    customer_id=customer_id
                ),
            }
        )

        for metrics_row in metrics_response:
            metrics = {
                "cost": float(getattr(metrics_row.metrics, "cost_micros", 0))
                / 1_000_000,
                "impressions": int(getattr(metrics_row.metrics, "impressions", 0)),
                "clicks": int(getattr(metrics_row.metrics, "clicks", 0)),
                "conversions": float(getattr(metrics_row.metrics, "conversions", 0)),
                "average_cpc": float(getattr(metrics_row.metrics, "average_cpc", 0))
                / 1_000_000,
            }
            logging.debug(f"    └── Retrieved metrics: {metrics}")
            return metrics

    except Exception as e:
        logging.error(f"    ⚠️  Error getting metrics: {str(e)}", exc_info=True)
        return {
            "cost": 0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "average_cpc": 0,
        }


@log_execution_time
async def get_manager_accounts(ga_client: GoogleAdsClient) -> List[Dict]:
    """Get all manager accounts with their child accounts.

    Args:
        ga_client: Google Ads API client

    Returns:
        List of manager accounts with their child accounts and metrics
    """
    logging.info("=== Getting Manager Accounts ===")
    logging.info("Getting manager accounts...")
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    manager_accounts = []
    total_accounts = len(accessible_customers.resource_names)
    processed = 0

    logging.info(f"├── Found {total_accounts} accessible accounts to process")

    for idx, resource_name in enumerate(accessible_customers.resource_names, 1):
        customer_id = resource_name.split("/")[-1]
        logging.info(f"├── [{idx}/{total_accounts}] Processing account: {customer_id}")

        try:
            response = ga_client.get_service("GoogleAdsService").search(
                request={
                    "customer_id": customer_id,
                    "query": build_account_query(customer_id, is_manager=True),
                }
            )

            for row in response:
                processed += 1
                manager_data = {
                    ACCOUNT_FIELDS["id"]: row.customer.id,
                    ACCOUNT_FIELDS["name"]: row.customer.descriptive_name,
                    ACCOUNT_FIELDS["currency"]: row.customer.currency_code,
                    ACCOUNT_FIELDS["timezone"]: row.customer.time_zone,
                    ACCOUNT_FIELDS["resource_name"]: resource_name,
                    ACCOUNT_FIELDS["auto_tagging"]: row.customer.auto_tagging_enabled,
                    ACCOUNT_FIELDS["status"]: row.customer.status.name,
                    ACCOUNT_FIELDS["is_test_account"]: row.customer.test_account,
                    ACCOUNT_FIELDS["pay_per_conversion_issues"]: [
                        reason.name
                        for reason in row.customer.pay_per_conversion_eligibility_failure_reasons
                    ],
                }

                logging.info(f"│   ├── Found manager account: {manager_data['name']}")
                logging.info(f"│   ├── Status: {manager_data['status']}")
                logging.info(f"│   └── Getting child accounts...")

                # Get child accounts
                children = await get_child_accounts(
                    ga_client, manager_data["customer_id"]
                )
                manager_data["child_accounts"] = children
                manager_data["child_count"] = len(children)

                # Log child account summary
                active_children = sum(
                    1 for c in children if c.get("metrics", {}).get("cost", 0) > 0
                )
                if children:
                    logging.info(
                        f"│       └── Found {len(children)} child accounts "
                        f"({active_children} active with spend)"
                    )

                manager_accounts.append(manager_data)

        except Exception as e:
            logging.error(
                f"│   ⚠️  Error processing manager {customer_id}: {str(e)}",
                exc_info=True,
            )

    logging.info(
        f"└── Completed processing {processed} manager accounts "
        f"(found {len(manager_accounts)} with {sum(m['child_count'] for m in manager_accounts)} total children)"
    )
    logging.info("=== Completed Manager Accounts ===")
    return manager_accounts


@log_execution_time
async def get_non_manager_accounts(ga_client: GoogleAdsClient) -> List[Dict]:
    """Get all non-manager accounts with their metrics.

    Args:
        ga_client: Google Ads API client

    Returns:
        List of non-manager accounts with their metrics
    """
    logging.info("=== Getting Non-Manager Accounts ===")
    logging.info("Getting non-manager accounts...")
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()
    total_accounts = len(accessible_customers.resource_names)
    client_accounts = []
    processed = 0

    logging.info(f"├── Found {total_accounts} accessible accounts to process")

    # First, get basic account info without metrics
    for idx, resource_name in enumerate(accessible_customers.resource_names, 1):
        customer_id = resource_name.split("/")[-1]
        logging.info(f"├── [{idx}/{total_accounts}] Processing account: {customer_id}")

        base_query = build_account_query(customer_id, is_manager=False)

        ga_service = ga_client.get_service("GoogleAdsService")
        try:
            response = ga_service.search(
                request={"customer_id": customer_id, "query": base_query}
            )

            for row in response:
                processed += 1
                client_data = {
                    ACCOUNT_FIELDS["id"]: row.customer.id,
                    ACCOUNT_FIELDS["name"]: row.customer.descriptive_name,
                    ACCOUNT_FIELDS["currency"]: row.customer.currency_code,
                    ACCOUNT_FIELDS["timezone"]: row.customer.time_zone,
                    ACCOUNT_FIELDS["resource_name"]: resource_name,
                    ACCOUNT_FIELDS["auto_tagging"]: row.customer.auto_tagging_enabled,
                    ACCOUNT_FIELDS["status"]: row.customer.status.name,
                    ACCOUNT_FIELDS["is_test_account"]: row.customer.test_account,
                    ACCOUNT_FIELDS["pay_per_conversion_issues"]: [
                        reason.name
                        for reason in row.customer.pay_per_conversion_eligibility_failure_reasons
                    ],
                }

                logging.info(f"│   ├── Found client account: {client_data['name']}")
                logging.info(f"│   ├── Status: {client_data['status']}")

                # Get metrics using helper function
                logging.info(f"│   └── Fetching metrics...")
                client_data["metrics"] = await get_metrics_for_account(
                    ga_service, str(row.customer.id)
                )

                if client_data["metrics"].get("cost", 0) > 0:
                    logging.info(
                        f"│       └── Active account with spend: {client_data['metrics']['cost']:.2f} "
                        f"({client_data['metrics']['clicks']} clicks)"
                    )

                client_accounts.append(client_data)

        except Exception as e:
            logging.error(
                f"│   ⚠️  Error processing client account {customer_id}: {str(e)}",
                exc_info=True,
            )

    logging.info(
        f"└── Completed processing {processed} client accounts "
        f"(found {len(client_accounts)} active accounts)"
    )
    logging.info("=== Completed Non-Manager Accounts ===")
    return client_accounts


async def get_all_accounts(ga_client: GoogleAdsClient) -> Dict:
    """Get both manager and non-manager accounts"""
    manager_accounts = await get_manager_accounts(ga_client)
    client_accounts = await get_non_manager_accounts(ga_client)

    return {
        "manager_accounts": manager_accounts,
        "client_accounts": client_accounts,
        "total_accounts": len(manager_accounts) + len(client_accounts),
    }


@log_execution_time
async def get_child_accounts(ga_client: GoogleAdsClient, manager_id: str) -> List:
    """Get all child accounts under a specific manager account"""
    logging.info(f"Getting child accounts for manager {manager_id}...")
    try:
        # First get basic account information
        base_query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.applied_labels,
                customer_client.client_customer,
                customer_client.level,
                customer_client.manager,
                customer_client.currency_code,
                customer_client.time_zone
            FROM customer_client
            WHERE customer_client.status = 'ENABLED'
            AND customer_client.id != {manager_id}
        """.format(
            manager_id=manager_id
        )

        ga_service = ga_client.get_service("GoogleAdsService")
        response = ga_service.search(
            request={"customer_id": str(manager_id), "query": base_query}
        )

        child_accounts = []
        for row in response:
            account_data = {
                "id": str(getattr(row.customer_client, "id", "")),
                "name": str(getattr(row.customer_client, "descriptive_name", "")),
                "applied_labels": [],
                "client_customer": str(
                    getattr(row.customer_client, "client_customer", "")
                ),
                "level": int(getattr(row.customer_client, "level", 0)),
                "is_manager": bool(getattr(row.customer_client, "manager", False)),
                "currency": str(getattr(row.customer_client, "currency_code", "")),
                "timezone": str(getattr(row.customer_client, "time_zone", "")),
            }

            # Process labels if available
            if labels := getattr(row.customer_client, "applied_labels", None):
                account_data["applied_labels"] = [
                    str(label) for label in labels if label
                ]

            # Get metrics for non-manager accounts using helper function
            if not account_data["is_manager"]:
                account_data["metrics"] = await get_metrics_for_account(
                    ga_service, account_data["id"]
                )

            child_accounts.append(account_data)

        logging.info(f"└── Completed processing {len(child_accounts)} child accounts")
        return child_accounts

    except Exception as e:
        logging.error(f"⚠️  Error getting child accounts: {str(e)}", exc_info=True)
        return []
