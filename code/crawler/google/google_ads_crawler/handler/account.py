import logging
from typing import Dict, List

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from .query import build_customer_client_query
from dependency.profile import log_execution_time


@log_execution_time
async def get_all_account_hierarchy(ga_client: GoogleAdsClient) -> List[Dict]:
    """Get all accessible accounts and their hierarchical structure.

    This function fetches all accounts the authenticated user has access to,
    and builds their complete hierarchical structure including child accounts.

    Args:
        ga_client: Google Ads API client

    Returns:
        List[AccountData]: List of accounts with their hierarchy, where each account contains:
            - customer_id: Account identifier
            - descriptive_name: Account name
            - currency_code: Account currency
            - time_zone: Account timezone
            - resource_name: Google Ads resource path
            - status: Account status (ENABLED, etc)
            - children: List of child accounts with same structure
            - child_count: Number of direct child accounts
    """
    logging.info("=== Getting Manager Accounts ===")
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    accounts = []
    total_accounts = len(accessible_customers.resource_names)
    processed = 0

    logging.info(f"├── Found {total_accounts} accessible accounts to process")

    for idx, resource_name in enumerate(accessible_customers.resource_names, 1):
        customer_id = resource_name.split("/")[-1]
        logging.info(f"├── [{idx}/{total_accounts}] Processing account: {customer_id}")

        try:
            # Get account hierarchy
            mcc_hierarchy = await get_account_hierarchy(ga_client, customer_id)
            if mcc_hierarchy:
                processed += 1

                # Convert hierarchy to manager data format
                customer_data = {
                    "customer_id": mcc_hierarchy["customer_id"],
                    "descriptive_name": mcc_hierarchy["descriptive_name"],
                    "currency_code": mcc_hierarchy["currency_code"],
                    "time_zone": mcc_hierarchy["time_zone"],
                    "client_customer": mcc_hierarchy["client_customer"],
                    "level": mcc_hierarchy["level"],
                    "manager": mcc_hierarchy["manager"],
                    "test_account": mcc_hierarchy["test_account"],
                    "resource_name": resource_name,
                    "status": mcc_hierarchy["status"],
                    "children": mcc_hierarchy["children"],
                    "child_count": len(mcc_hierarchy["children"]),
                }

                logging.info(
                    f"│   ├── Found account: {customer_data['descriptive_name']}"
                )
                logging.info(f"│   ├── Status: {customer_data['status']}")

                if customer_data["child_count"] > 0:
                    logging.info(
                        f"│       └── Found {customer_data['child_count']} child accounts"
                    )

                accounts.append(customer_data)

        except Exception as e:
            if "CUSTOMER_NOT_ENABLED" in str(e):
                logging.warning(f"│   ⚠️  Account {customer_id} is not enabled")
            elif "PERMISSION_DENIED" in str(e):
                logging.warning(f"│   ⚠️  No permission to access account {customer_id}")
            else:
                logging.error(
                    f"│   ⚠️  Error processing account {customer_id}: {str(e)}",
                    exc_info=True,
                )
            continue

    logging.info(f"└── Completed processing {processed}/{total_accounts} accounts")
    logging.info(f"   └── Total accounts with hierarchy: {len(accounts)}")
    logging.info("=== Completed Account Hierarchy ===")

    return accounts


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
    cc_query = build_customer_client_query("customer_client.level <= 1")

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
                            "test_account": customer_client.test_account,
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
                    "test_account": customer_client.test_account,
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
        logging.error(
            f"⚠️  Error processing hierarchy for {manager_id}: {str(e)}", exc_info=True
        )
        return None

    logging.info(f"=== Completed Account Hierarchy for MCC {manager_id} ===")
    return root_customer_client


def build_hierarchy_tree(node: Dict, customer_ids_to_children: Dict) -> None:
    """Recursively build hierarchy tree.

    Args:
        node: Current node in hierarchy
        customer_ids_to_children: Dict mapping customer IDs to their children
    """
    if node["customer_id"] in customer_ids_to_children:
        node["children"] = customer_ids_to_children[node["customer_id"]]
        for child in node["children"]:
            build_hierarchy_tree(child, customer_ids_to_children)
