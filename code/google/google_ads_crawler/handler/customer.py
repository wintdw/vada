import logging

from google.ads.googleads.client import GoogleAdsClient  # type: ignore


async def get_manager_accounts(ga_client: GoogleAdsClient) -> list:
    """Fetch list of manager accounts with their child accounts"""
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    manager_accounts = []

    for resource_name in accessible_customers.resource_names:
        customer_id = resource_name.split("/")[-1]

        query = """
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
            AND customer.manager = TRUE
        """.format(
            customer_id=customer_id
        )

        ga_service = ga_client.get_service("GoogleAdsService")
        try:
            response = ga_service.search(
                request={"customer_id": customer_id, "query": query}
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

                # Get child accounts
                child_accounts = await get_child_accounts(ga_client, customer_id)
                manager_data["child_accounts"] = child_accounts
                manager_data["child_accounts_count"] = len(child_accounts)

                manager_accounts.append(manager_data)

        except Exception as e:
            logging.warning(f"Error processing manager account {customer_id}: {str(e)}")

    return manager_accounts


async def get_non_manager_accounts(ga_client: GoogleAdsClient) -> list:
    """Fetch list of non-manager accounts with metrics"""
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    client_accounts = []

    for resource_name in accessible_customers.resource_names:
        customer_id = resource_name.split("/")[-1]

        query = """
            SELECT 
                customer.id,
                customer.descriptive_name,
                customer.currency_code,
                customer.time_zone,
                customer.auto_tagging_enabled,
                customer.status,
                customer.manager,
                customer.test_account,
                customer.pay_per_conversion_eligibility_failure_reasons,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.average_cpc
            FROM customer 
            WHERE customer.id = '{customer_id}'
            AND customer.manager = FALSE
        """.format(
            customer_id=customer_id
        )

        ga_service = ga_client.get_service("GoogleAdsService")
        try:
            response = ga_service.search(
                request={"customer_id": customer_id, "query": query}
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
                    "metrics": {
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "conversions": row.metrics.conversions,
                        "average_cpc": (
                            row.metrics.average_cpc / 1_000_000
                            if row.metrics.average_cpc
                            else 0
                        ),
                    },
                }

                client_accounts.append(client_data)

        except Exception as e:
            logging.warning(f"Error processing client account {customer_id}: {str(e)}")

    return client_accounts


# Helper function to combine both results if needed
async def get_all_accounts(ga_client: GoogleAdsClient) -> dict:
    """Get both manager and non-manager accounts"""
    manager_accounts = await get_manager_accounts(ga_client)
    client_accounts = await get_non_manager_accounts(ga_client)

    return {
        "manager_accounts": manager_accounts,
        "client_accounts": client_accounts,
        "total_accounts": len(manager_accounts) + len(client_accounts),
    }
