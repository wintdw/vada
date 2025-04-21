import logging
from typing import Dict, List
from functools import wraps
from time import time

from google.ads.google_ads.client import GoogleAdsClient  # type: ignore


def log_execution_time(func):
    """Decorator to log function execution time"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        result = await func(*args, **kwargs)
        execution_time = time() - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result

    return wrapper


@log_execution_time
async def get_metrics_for_account(ga_service, customer_id: str) -> dict:
    """Helper function to get metrics for an account"""
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
async def get_manager_accounts(ga_client: GoogleAdsClient) -> List:
    """Fetch list of manager accounts with their child accounts"""
    logging.info("Getting manager accounts...")
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    manager_accounts = []
    total_accounts = len(accessible_customers.resource_names)
    logging.info(f"├── Found {total_accounts} accessible accounts")

    for idx, resource_name in enumerate(accessible_customers.resource_names, 1):
        customer_id = resource_name.split("/")[-1]
        logging.info(f"├── Processing account {idx}/{total_accounts}: {customer_id}")

        try:
            response = ga_client.get_service("GoogleAdsService").search(
                request={
                    "customer_id": customer_id,
                    "query": """
                    SELECT customer.id, customer.descriptive_name, 
                           customer.currency_code, customer.time_zone
                    FROM customer 
                    WHERE customer.id = '{customer_id}'
                    AND customer.manager = TRUE
                """.format(
                        customer_id=customer_id
                    ),
                }
            )

            for row in response:
                manager_data = {
                    "customer_id": row.customer.id,
                    "name": row.customer.descriptive_name,
                    "currency": row.customer.currency_code,
                    "timezone": row.customer.time_zone,
                    "resource_name": resource_name,
                    "auto_tagging": row.customer.auto_tagging_enabled,
                    "status": row.customer.status.name,
                    "is_test_account": row.customer.test_account,
                    "pay_per_conversion_issues": [
                        reason.name
                        for reason in row.customer.pay_per_conversion_eligibility_failure_reasons
                    ],
                }
                logging.info(f"│   └── Found manager account: {manager_data['name']}")
                manager_accounts.append(manager_data)

        except Exception as e:
            logging.error(
                f"│   ⚠️  Error processing manager {customer_id}: {str(e)}",
                exc_info=True,
            )

    logging.info(f"└── Completed processing {len(manager_accounts)} manager accounts")
    return manager_accounts


@log_execution_time
async def get_non_manager_accounts(ga_client: GoogleAdsClient) -> List:
    """Fetch list of non-manager accounts with metrics"""
    logging.info("Getting non-manager accounts...")
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()
    client_accounts = []

    # First, get basic account info without metrics
    for resource_name in accessible_customers.resource_names:
        customer_id = resource_name.split("/")[-1]

        base_query = """
            SELECT 
                customer.id,
                customer.descriptive_name,
                customer.currency_code,
                customer.time_zone,
                customer.auto_tagging_enabled,
                customer.status,
                customer.manager,
                customer.test_account,
                customer.pay_per_conversion_eligibility_failure_reasons
            FROM customer 
            WHERE customer.id = '{customer_id}'
            AND customer.manager = FALSE
        """.format(
            customer_id=customer_id
        )

        ga_service = ga_client.get_service("GoogleAdsService")
        try:
            response = ga_service.search(
                request={"customer_id": customer_id, "query": base_query}
            )

            for row in response:
                client_data = {
                    "customer_id": row.customer.id,
                    "name": row.customer.descriptive_name,
                    "currency": row.customer.currency_code,
                    "timezone": row.customer.time_zone,
                    "resource_name": resource_name,
                    "auto_tagging": row.customer.auto_tagging_enabled,
                    "status": row.customer.status.name,
                    "is_test_account": row.customer.test_account,
                    "pay_per_conversion_issues": [
                        reason.name
                        for reason in row.customer.pay_per_conversion_eligibility_failure_reasons
                    ],
                }

                # Get metrics using helper function
                client_data["metrics"] = await get_metrics_for_account(
                    ga_service, str(row.customer.id)
                )

                client_accounts.append(client_data)

        except Exception as e:
            logging.error(
                f"Error processing client account {customer_id}: {str(e)}",
                exc_info=True,
            )

    return client_accounts


# Helper function to combine both results if needed
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
