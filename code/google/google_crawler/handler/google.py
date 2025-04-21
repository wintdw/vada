import logging

from google.ads.googleads.client import GoogleAdsClient  # type: ignore
from google.ads.googleads.v19.services.types.google_ads_service import (  # type: ignore
    SearchGoogleAdsRequest,
)


async def get_child_accounts(ga_client: GoogleAdsClient, customer_id: str):
    """Get all child accounts for a manager account"""
    try:
        query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.applied_labels,
                customer_client.client_customer,
                customer_client.level,
                customer_client.manager
            FROM customer_client
            WHERE customer_client.status = 'ENABLED'
        """

        ga_service = ga_client.get_service("GoogleAdsService")
        search_request = SearchGoogleAdsRequest(
            customer_id=customer_id,
            query=query,
        )
        response = ga_service.search(request=search_request)

        child_accounts = []
        for row in response:
            child_accounts.append(
                {
                    "id": row.customer_client.id,
                    "name": row.customer_client.descriptive_name,
                    "applied_labels": [
                        label for label in row.customer_client.applied_labels
                    ],
                    "client_customer": row.customer_client.client_customer,
                    "level": row.customer_client.level,
                    "is_manager": row.customer_client.manager,
                }
            )

        return child_accounts
    except Exception as e:
        logging.warning(f"Error getting child accounts for {customer_id}: {str(e)}")
        return []


async def get_customer_list(ga_client: GoogleAdsClient):
    """Fetch list of accessible customers with details"""
    customer_service = ga_client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    customers = []
    for resource_name in accessible_customers.resource_names:
        customer_id = resource_name.split("/")[-1]

        # Query without metrics for manager accounts
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
        """.format(
            customer_id=customer_id
        )

        # Query with metrics for non-manager accounts
        metrics_query = """
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
        """.format(
            customer_id=customer_id
        )

        ga_service = ga_client.get_service("GoogleAdsService")
        try:
            # First try with base query (no metrics)
            response = ga_service.search(
                request={"customer_id": customer_id, "query": base_query}
            )

            for row in response:
                customer_data = {
                    "customer_id": row.customer.id,
                    "name": row.customer.descriptive_name,
                    "currency": row.customer.currency_code,
                    "timezone": row.customer.time_zone,
                    "resource_name": resource_name,
                    "auto_tagging": row.customer.auto_tagging_enabled,
                    "status": row.customer.status.name,
                    "is_manager": row.customer.manager,
                    "is_test_account": row.customer.test_account,
                    "pay_per_conversion_issues": [
                        reason.name
                        for reason in row.customer.pay_per_conversion_eligibility_failure_reasons
                    ],
                }

                # If not a manager account, try to get metrics
                if not row.customer.manager:
                    try:
                        metrics_response = ga_service.search(
                            request={
                                "customer_id": customer_id,
                                "query": metrics_query,
                            }
                        )
                        for metrics_row in metrics_response:
                            customer_data["metrics"] = {
                                "cost": metrics_row.metrics.cost_micros / 1_000_000,
                                "impressions": metrics_row.metrics.impressions,
                                "clicks": metrics_row.metrics.clicks,
                                "conversions": metrics_row.metrics.conversions,
                                "average_cpc": (
                                    metrics_row.metrics.average_cpc / 1_000_000
                                    if metrics_row.metrics.average_cpc
                                    else 0
                                ),
                            }
                    except Exception as metrics_error:
                        logging.warning(
                            f"Could not fetch metrics for {customer_id}: {str(metrics_error)}"
                        )

                # Get child accounts if this is a manager account
                if row.customer.manager:
                    child_accounts = await get_child_accounts(ga_client, customer_id)
                    customer_data["child_accounts"] = child_accounts

                customers.append(customer_data)

        except Exception as e:
            logging.warning(f"Error processing customer {customer_id}: {str(e)}")
            customers.append(
                {
                    "customer_id": customer_id,
                    "resource_name": resource_name,
                    "error": str(e),
                }
            )

    return customers


async def get_google_ads_reports(client: GoogleAdsClient, start_date, end_date):
    """Fetch Google Ads reports for all accessible customers"""
    query = """
        SELECT
            customer.id,
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    """.format(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    ga_service = client.get_service("GoogleAdsService")
    results = []

    # First, get all accessible customers
    customer_service = client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()

    for resource_name in accessible_customers.resource_names:
        customer_id = resource_name.split("/")[-1]
        logging.info(f"Processing customer ID: {customer_id}")

        try:
            # Check if this is a manager account by looking for child accounts
            child_accounts = await get_child_accounts(client, customer_id)

            if child_accounts:
                logging.info(
                    f"Found manager account {customer_id} with {len(child_accounts)} child accounts"
                )
                # Process each non-manager child account
                for child in child_accounts:
                    if not child["is_manager"]:
                        try:
                            logging.info(
                                f"Fetching reports for child account {child['customer_id']}"
                            )
                            search_request = SearchGoogleAdsRequest(
                                customer_id=child["customer_id"],
                                query=query,
                            )
                            response = ga_service.search(request=search_request)

                            for row in response:
                                results.append(
                                    {
                                        "customer_id": child["customer_id"],
                                        "customer_name": child["name"],
                                        "manager_id": customer_id,
                                        "campaign_id": row.campaign.id,
                                        "campaign_name": row.campaign.name,
                                        "status": row.campaign.status.name,
                                        "impressions": row.metrics.impressions,
                                        "clicks": row.metrics.clicks,
                                        "cost": row.metrics.cost_micros / 1_000_000,
                                        "conversions": row.metrics.conversions,
                                    }
                                )
                        except Exception as e:
                            logging.warning(
                                f"Error fetching reports for child account {child['customer_id']}: {str(e)}"
                            )
                            continue
            else:
                # Try to get metrics directly (only works for non-manager accounts)
                try:
                    logging.info(f"Fetching reports for direct account {customer_id}")
                    search_request = SearchGoogleAdsRequest(
                        customer_id=customer_id,
                        query=query,
                    )
                    response = ga_service.search(request=search_request)

                    for row in response:
                        results.append(
                            {
                                "customer_id": customer_id,
                                "campaign_id": row.campaign.id,
                                "campaign_name": row.campaign.name,
                                "status": row.campaign.status.name,
                                "impressions": row.metrics.impressions,
                                "clicks": row.metrics.clicks,
                                "cost": row.metrics.cost_micros / 1_000_000,
                                "conversions": row.metrics.conversions,
                            }
                        )
                except Exception as e:
                    if "REQUESTED_METRICS_FOR_MANAGER" in str(e):
                        logging.info(
                            f"Skipping manager account {customer_id} with no child accounts"
                        )
                    else:
                        logging.warning(
                            f"Error processing account {customer_id}: {str(e)}"
                        )
                    continue

        except Exception as e:
            logging.warning(f"Error processing customer {customer_id}: {str(e)}")
            continue

    return results
