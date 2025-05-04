"""
https://github.com/googleapis/googleapis/blob/master/google/ads/googleads/v17/enums/customer_status.proto
Customer Status:
    UNSPECIFIED = 0;

    // Used for return value only. Represents value unknown in this version.
    UNKNOWN = 1;

    // Indicates an active account able to serve ads.
    ENABLED = 2;

    // Indicates a canceled account unable to serve ads.
    // Can be reactivated by an admin user.
    CANCELED = 3;

    // Indicates a suspended account unable to serve ads.
    // May only be activated by Google support.
    SUSPENDED = 4;

    // Indicates a closed account unable to serve ads.
    // Test account will also have CLOSED status.
    // Status is permanent and may not be reopened.
    CLOSED = 5;
"""

import logging
from typing import Dict, List

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from .query import build_customer_client_query
from dependency.profile import log_execution_time


@log_execution_time
async def get_all_account_hierarchies(ga_client: GoogleAdsClient) -> List[Dict]:
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

    account_hiers = []
    total_accounts = len(accessible_customers.resource_names)
    processed = 0

    logging.info(f"├── Found {total_accounts} accessible accounts to process")

    for idx, resource_name in enumerate(accessible_customers.resource_names, 1):
        customer_id = resource_name.split("/")[-1]
        logging.info(f"├── [{idx}/{total_accounts}] Processing account: {customer_id}")

        try:
            # Get account hierarchy
            root_hierarchy = await get_account_hierarchy(ga_client, customer_id)
            if root_hierarchy:
                processed += 1

                # Convert hierarchy to manager data format
                customer_data = {
                    "customer_id": root_hierarchy["customer_id"],
                    "descriptive_name": root_hierarchy["descriptive_name"],
                    "currency_code": root_hierarchy["currency_code"],
                    "time_zone": root_hierarchy["time_zone"],
                    "client_customer": root_hierarchy["client_customer"],
                    "level": root_hierarchy["level"],
                    "manager": root_hierarchy["manager"],
                    "test_account": root_hierarchy["test_account"],
                    "status": root_hierarchy["status"],
                    "children": root_hierarchy["children"],
                    "child_count": len(root_hierarchy["children"]),
                }

                logging.info(
                    f"│   ├── Found account: {customer_data['descriptive_name']}"
                )
                logging.info(f"│   ├── Status: {customer_data['status']}")

                if customer_data["child_count"] > 0:
                    logging.info(
                        f"│       └── Found {customer_data['child_count']} child accounts"
                    )

                account_hiers.append(customer_data)

        except Exception as e:
            logging.error(
                f"│   ⚠️  Error processing account {customer_id}: {str(e)}",
                exc_info=True,
            )
            continue

    logging.info(f"└── Completed processing {processed}/{total_accounts} accounts")
    logging.info(f"   └── Total accounts with hierarchy: {len(account_hiers)}")
    logging.info("=== Completed Account Hierarchy ===")

    return account_hiers


async def get_account_hierarchy(ga_client: GoogleAdsClient, account_id: str) -> Dict:
    """Get full hierarchy of a Google Ads account with unlimited nesting levels.

    Performs breadth-first traversal of the account hierarchy, handling both manager
    and non-manager accounts at any level. Uses parent-child relationships to build
    a complete tree structure.

    Args:
        ga_client: Google Ads API client with authentication configured
        account_id: ID of the root account to start hierarchy traversal from

    Returns:
        Dict containing account hierarchy with structure:
            {
                "customer_id": str,
                "descriptive_name": str,
                "currency_code": str,
                "time_zone": str,
                "client_customer": str,
                "level": int,
                "status": int,
                "manager": bool,
                "test_account": bool,
                "children": List[Dict],  # Recursive structure
                "child_count": int
            }

    Raises:
        Exception: For API errors (customer not enabled, permission denied, etc.)
    """
    logging.info(f"=== Getting Account Hierarchy for {account_id} ===")

    # Remove level restriction to allow deeper nesting
    cc_query = build_customer_client_query()

    # Track parent-child relationships
    parent_map = {}
    unprocessed_customer_ids = [(account_id, None)]  # (customer_id, parent_id)
    customer_ids_to_children = {}
    root_customer_client = None
    processed_ids = set()

    logging.debug(f"├── Starting BFS traversal with root: {account_id}")
    processed_count = 0

    while unprocessed_customer_ids:
        customer_id, parent_id = unprocessed_customer_ids.pop(0)
        customer_id = str(customer_id)

        if customer_id in processed_ids:
            continue

        processed_ids.add(customer_id)
        logging.debug(
            f"│   ├── Processing customer: {customer_id} (Parent: {parent_id})"
        )

        try:
            # Set login_customer_id to root for all queries
            ga_client.login_customer_id = str(account_id)
            googleads_service = ga_client.get_service("GoogleAdsService")

            response = googleads_service.search(customer_id=customer_id, query=cc_query)

            for row in response:
                customer_client = row.customer_client
                processed_count += 1

                # Handle root account
                if customer_client.level == 0:
                    if root_customer_client is None:
                        root_customer_client = {
                            "customer_id": str(customer_client.id),
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

                # Store parent relationship
                if parent_id:
                    parent_map[str(customer_client.id)] = str(parent_id)

                # Handle child accounts
                parent_key = str(parent_id) if parent_id else str(account_id)
                if parent_key not in customer_ids_to_children:
                    customer_ids_to_children[parent_key] = []

                child_data = {
                    "customer_id": str(customer_client.id),
                    "descriptive_name": customer_client.descriptive_name,
                    "currency_code": customer_client.currency_code,
                    "time_zone": customer_client.time_zone,
                    "client_customer": customer_client.client_customer,
                    "level": customer_client.level,
                    "status": customer_client.status,
                    "manager": customer_client.manager,
                    "test_account": customer_client.test_account,
                }

                customer_ids_to_children[parent_key].append(child_data)

                # Queue manager accounts with their parent
                if (
                    customer_client.manager
                    and str(customer_client.id) not in processed_ids
                ):
                    unprocessed_customer_ids.append(
                        (str(customer_client.id), customer_id)
                    )
                    logging.debug(
                        f"│   │   │   └── Queued manager account for processing: "
                        f"{customer_client.id} (Level: {customer_client.level}, "
                        f"Parent: {customer_id})"
                    )

        except Exception as search_error:
            if "CUSTOMER_NOT_ENABLED" in str(search_error):
                logging.warning(f"│   ⚠️  Account {customer_id} is not enabled")
            elif "PERMISSION_DENIED" in str(search_error):
                logging.warning(f"│   ⚠️  No permission to access account {customer_id}")
            else:
                logging.error(
                    f"│   │   ⚠️  Error searching customer {customer_id}: {str(search_error)}",
                    exc_info=True,
                )
            continue

    logging.debug(f"├── Processed {processed_count} total accounts")

    # Build hierarchy using parent relationships
    def build_hierarchy_tree(node: Dict, customer_ids_to_children: Dict) -> None:
        node_id = str(node["customer_id"])
        if "children" not in node:
            node["children"] = []

        if node_id in customer_ids_to_children:
            children = customer_ids_to_children[node_id]
            for child in children:
                if "children" not in child:
                    child["children"] = []
                node["children"].append(child)

                # Only process if this child has children
                child_id = str(child["customer_id"])
                if child_id in customer_ids_to_children:
                    build_hierarchy_tree(child, customer_ids_to_children)

            node["child_count"] = len(node["children"])

    if root_customer_client:
        logging.debug("├── Building hierarchy tree")
        build_hierarchy_tree(root_customer_client, customer_ids_to_children)
        logging.debug(
            f"└── Built tree with {len(root_customer_client['children'])} "
            f"direct children"
        )
    else:
        logging.warning(f"└── No root account found for {account_id}")
        return None

    logging.info(f"=== Completed Account Hierarchy for {account_id} ===")
    return root_customer_client
