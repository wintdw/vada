import logging

from google.ads.googleads.client import GoogleAdsClient  # type: ignore
from google.ads.googleads.v19.services.types.google_ads_service import (  # type: ignore
    SearchGoogleAdsRequest,
)

from .customer import get_child_accounts


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
