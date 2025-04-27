import logging
from typing import Dict, List

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from .query import build_customer_query, build_customer_client_query
from dependency.profile import log_execution_time


@log_execution_time
async def get_manager_accounts(ga_client: GoogleAdsClient) -> List[Dict]:
    """Get all manager accounts with their child accounts.

    Args:
        ga_client: Google Ads API client

    Returns:
        List of manager accounts with their child accounts
    """
    logging.info("=== Getting Manager Accounts ===")
    logging.info("Getting manager accounts...")
    googleads_service = ga_client.get_service("GoogleAdsService")
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
            response = googleads_service.search(
                customer_id=customer_id,
                query=build_customer_query(customer_id, is_manager=True),
            )

            for row in response:
                logging.debug(f"│   ├── Row content: {row}")
                processed += 1
                manager_data = {
                    "customer_id": row.customer.id,
                    "descriptive_name": row.customer.descriptive_name,
                    "currency_code": row.customer.currency_code,
                    "time_zone": row.customer.time_zone,
                    "resource_name": resource_name,
                    "auto_tagging_enabled": row.customer.auto_tagging_enabled,
                    "status": row.customer.status.name,
                    "is_test_account": row.customer.test_account,
                }

                logging.info(
                    f"│   ├── Found manager account: {manager_data['descriptive_name']}"
                )
                logging.info(f"│   ├── Status: {manager_data['status']}")
                logging.info(f"│   └── Getting child accounts...")

                try:
                    # Get child accounts
                    children = await get_child_accounts(
                        ga_client, manager_data["customer_id"]
                    )
                    manager_data["child_accounts"] = children
                    manager_data["child_count"] = len(children)

                    # Log child account summary
                    if children:
                        logging.info(
                            f"│       └── Found {len(children)} child accounts"
                        )

                except Exception as child_error:
                    if "CUSTOMER_NOT_ENABLED" in str(child_error):
                        logging.warning(
                            f"│   ⚠️  Manager account {customer_id} is not enabled"
                        )
                    elif "PERMISSION_DENIED" in str(child_error):
                        logging.warning(
                            f"│   ⚠️  No permission to access manager {customer_id}"
                        )
                    else:
                        logging.error(
                            f"│   ⚠️  Error getting child accounts for {customer_id}: {str(child_error)}"
                        )
                    manager_data["child_accounts"] = []
                    manager_data["child_count"] = 0
                    manager_data["error"] = str(child_error)

                manager_accounts.append(manager_data)

        except Exception as e:
            if "CUSTOMER_NOT_ENABLED" in str(e):
                logging.warning(f"│   ⚠️  Account {customer_id} is not enabled")
            elif "PERMISSION_DENIED" in str(e):
                logging.warning(f"│   ⚠️  No permission to access account {customer_id}")
            else:
                logging.error(
                    f"│   ⚠️  Error processing manager {customer_id}: {str(e)}",
                    exc_info=True,
                )
            continue

    logging.info(
        f"└── Completed processing {processed} manager accounts "
        f"(found {len(manager_accounts)} with {sum(m['child_count'] for m in manager_accounts)} total children)"
    )
    logging.info("=== Completed Manager Accounts ===")
    return manager_accounts


@log_execution_time
async def get_non_manager_accounts(ga_client: GoogleAdsClient) -> List[Dict]:
    """Get all non-manager accounts.

    Args:
        ga_client: Google Ads API client

    Returns:
        List of non-manager accounts
    """
    logging.info("=== Getting Non-Manager Accounts ===")
    logging.info("Getting non-manager accounts...")

    googleads_service = ga_client.get_service("GoogleAdsService")
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

        try:
            response = googleads_service.search(
                customer_id=customer_id,
                query=build_customer_query(customer_id, is_manager=False),
            )

            for row in response:
                logging.debug(f"│   ├── Row content: {row}")
                processed += 1
                client_data = {
                    "customer_id": row.customer.id,
                    "descriptive_name": row.customer.descriptive_name,
                    "currency_code": row.customer.currency_code,
                    "time_zone": row.customer.time_zone,
                    "resource_name": resource_name,
                    "auto_tagging_enabled": row.customer.auto_tagging_enabled,
                    "status": row.customer.status.name,
                    "is_test_account": row.customer.test_account,
                }

                logging.info(
                    f"│   ├── Found client account: {client_data['descriptive_name']}"
                )
                logging.info(f"│   ├── Status: {client_data['status']}")

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
    """Get all child accounts under a specific manager account.

    Args:
        ga_client: Google Ads API client
        manager_id: ID of the manager account

    Returns:
        List of child accounts
    """
    logging.info(f"Getting child accounts for manager {manager_id}...")
    try:
        googleads_service = ga_client.get_service("GoogleAdsService")
        response = googleads_service.search(
            customer_id=manager_id, query=build_customer_client_query(manager_id)
        )

        child_accounts = []
        for row in response:
            logging.debug(f"│   ├── Row content: {row}")
            account_data = {
                "customer_id": row.customer_client.id,
                "descriptive_name": row.customer_client.descriptive_name,
                "currency_code": row.customer_client.currency_code,
                "time_zone": row.customer_client.time_zone,
                "client_customer": row.customer_client.client_customer,
                "level": row.customer_client.level,
                "status": row.customer_client.status,
                "manager": row.customer_client.manager,
                "currency_code": row.customer_client.currency_code,
                "time_zone": row.customer_client.time_zone,
            }

            child_accounts.append(account_data)

        logging.info(f"└── Completed processing {len(child_accounts)} child accounts")
        return child_accounts

    except Exception as e:
        logging.error(f"⚠️  Error getting child accounts: {str(e)}", exc_info=True)
        return []
