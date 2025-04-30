import logging
from typing import Dict, List

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from .query import build_customer_query, build_customer_client_query
from dependency.profile import log_execution_time


@log_execution_time
async def get_manager_accounts(ga_client: GoogleAdsClient) -> List[Dict]:
    """Get all manager accounts with their hierarchy.

    Args:
        ga_client: Google Ads API client

    Returns:
        List[Dict]: List of manager accounts with their hierarchical structure
    """
    logging.info("=== Getting Manager Accounts ===")
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
            # Get account hierarchy
            hierarchy = await get_account_hierarchy(ga_client, customer_id)
            if hierarchy:
                processed += 1

                # Convert hierarchy to manager data format
                manager_data = {
                    "customer_id": hierarchy["customer_id"],
                    "descriptive_name": hierarchy["descriptive_name"],
                    "currency_code": hierarchy["currency_code"],
                    "time_zone": hierarchy["time_zone"],
                    "resource_name": resource_name,
                    "status": hierarchy["status"],
                    "child_accounts": hierarchy["children"],
                    "child_count": len(hierarchy["children"]),
                }

                logging.info(
                    f"│   ├── Found manager account: {manager_data['descriptive_name']}"
                )
                logging.info(f"│   ├── Status: {manager_data['status']}")

                if manager_data["child_count"] > 0:
                    logging.info(
                        f"│       └── Found {manager_data['child_count']} child accounts"
                    )

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
                customer_id=str(customer_id),
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
            customer_id=str(manager_id), query=build_customer_client_query()
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
            }

            child_accounts.append(account_data)

        logging.info(f"└── Completed processing {len(child_accounts)} child accounts")
        return child_accounts

    except Exception as e:
        logging.error(f"⚠️  Error getting child accounts: {str(e)}", exc_info=True)
        return []


@log_execution_time
async def get_account_hierarchy(ga_client: GoogleAdsClient, manager_id: str) -> Dict:
    """Get full hierarchy of a MCC account.

    Args:
        ga_client: Google Ads API client
        manager_id: ID of the manager account to start hierarchy from

    Returns:
        Dict containing account hierarchy with structure:
        {
            "customer_id": str,
            "descriptive_name": str,
            "currency_code": str,
            "time_zone": str,
            "status": str,
            "manager": bool,
            "children": List[Dict]  # recursive structure
        }
    """
    logging.info("=== Getting Account Hierarchy ===")

    googleads_service = ga_client.get_service("GoogleAdsService")

    # Build query for child accounts
    cc_query = build_customer_client_query(manager_id, "customer_client.level <= 1")

    try:
        # Perform breadth-first search
        # Initialize queue with the root manager account
        unprocessed_customer_ids = [manager_id]
        customer_ids_to_children = {}
        root_customer_client = None

        while unprocessed_customer_ids:
            customer_id = unprocessed_customer_ids.pop(0)
            response = googleads_service.search(
                customer_id=str(customer_id), query=cc_query
            )

            for row in response:
                customer_client = row.customer_client

                # Store root customer
                if customer_client.level == 0:
                    if root_customer_client is None:
                        root_customer_client = {
                            "customer_id": customer_client.id,
                            "descriptive_name": customer_client.descriptive_name,
                            "currency_code": customer_client.currency_code,
                            "time_zone": customer_client.time_zone,
                            "client_customer": customer_client.client_customer,
                            "level": customer_client.level,
                            "status": customer_client.status,
                            "manager": customer_client.manager,
                            "children": [],
                        }
                    continue

                # Store child accounts
                if customer_id not in customer_ids_to_children:
                    customer_ids_to_children[customer_id] = []

                child_data = {
                    "customer_id": customer_client.id,
                    "descriptive_name": customer_client.descriptive_name,
                    "currency_code": customer_client.currency_code,
                    "time_zone": customer_client.time_zone,
                    "client_customer": customer_client.client_customer,
                    "level": customer_client.level,
                    "status": customer_client.status,
                    "manager": customer_client.manager,
                    "currency_code": customer_client.currency_code,
                    "time_zone": customer_client.time_zone,
                }

                customer_ids_to_children[customer_id].append(child_data)

                # Add manager accounts to be processed
                if customer_client.manager and customer_client.level == 1:
                    if customer_client.id not in customer_ids_to_children:
                        unprocessed_customer_ids.append(customer_client.id)

        # Build hierarchy tree
        if root_customer_client:
            build_hierarchy_tree(root_customer_client, customer_ids_to_children)

    except Exception as e:
        logging.error(f"Error processing hierarchy for {manager_id}: {str(e)}")
        return None

    logging.info(f"=== Completed Account Hierarchy for MCC {manager_id} ===")
    return root_customer_client


def build_hierarchy_tree(node: Dict, customer_ids_to_children: Dict) -> None:
    """Recursively build hierarchy tree.

    Args:
        node: Current node in hierarchy
        customer_ids_to_children: Dict mapping customer IDs to their children
    """
    if node["id"] in customer_ids_to_children:
        node["children"] = customer_ids_to_children[node["id"]]
        for child in node["children"]:
            build_hierarchy_tree(child, customer_ids_to_children)
