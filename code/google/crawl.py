import os
import logging
import json

# Set environment variable to disable OAuth token scope warning
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

from fastapi import FastAPI, HTTPException, Request, Body, Depends
from fastapi.responses import RedirectResponse
import hashlib
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Rename the import to avoid conflicts with FastAPI's Request
from google.auth.transport.requests import Request as GoogleRequest
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v19.services.types.google_ads_service import (
    SearchGoogleAdsRequest,
)

app = FastAPI(title="Google OAuth API")

# Store the flow object in a global variable or use a more robust solution like a database in production
flows = {}


class TokenRequest(BaseModel):
    refresh_token: str
    client_id: str
    client_secret: str
    token_uri: Optional[str] = "https://oauth2.googleapis.com/token"


@app.get("/")
async def root():
    return {
        "message": "Google OAuth API is running. Use /auth/url to get authorization URL."
    }


@app.get("/auth/url")
async def get_auth_url():
    """Generate and return a Google OAuth authorization URL"""
    try:
        scopes = ["https://www.googleapis.com/auth/adwords"]
        client_secrets_path = "client_secret_960285879954-o9dm5719frfvuqd7j4bbvm962gg1577g.apps.googleusercontent.com.json"
        redirect_uri = "https://google.vadata.vn/connector/google/auth"

        # Generate a secure random state value
        passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

        # Create OAuth flow
        flow = Flow.from_client_secrets_file(client_secrets_path, scopes=scopes)
        flow.redirect_uri = redirect_uri

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            state=passthrough_val,
            prompt="consent",
            include_granted_scopes="true",
        )

        # Store the flow object using the state as a key
        flows[state] = flow

        return {"authorization_url": authorization_url, "state": state}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating authorization URL: {str(e)}"
        )


async def get_child_accounts(client, customer_id):
    """Get all child accounts for a manager account"""
    try:
        query = """
            SELECT
                customer_client.client_customer,
                customer_client.level,
                customer_client.manager,
                customer_client.descriptive_name,
                customer_client.currency_code,
                customer_client.time_zone
            FROM customer_client
            WHERE customer_client.status = 'ENABLED'
        """

        ga_service = client.get_service("GoogleAdsService")
        search_request = SearchGoogleAdsRequest(
            customer_id=customer_id,
            query=query,
        )
        response = ga_service.search(request=search_request)

        child_accounts = []
        for row in response:
            child_accounts.append(
                {
                    "customer_id": row.customer_client.client_customer.split("/")[1],
                    "name": row.customer_client.descriptive_name,
                    "currency": row.customer_client.currency_code,
                    "timezone": row.customer_client.time_zone,
                    "is_manager": row.customer_client.manager,
                    "level": row.customer_client.level,
                }
            )

        return child_accounts
    except Exception as e:
        logging.warning(f"Error getting child accounts for {customer_id}: {str(e)}")
        return []


async def get_google_ads_reports(client, start_date, end_date):
    """Fetch Google Ads reports for all accessible customers"""
    try:
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
                        logging.info(
                            f"Fetching reports for direct account {customer_id}"
                        )
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

    except Exception as e:
        logging.error(f"Error fetching reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")


async def get_customer_list(client):
    """Fetch list of accessible customers with details"""
    try:
        customer_service = client.get_service("CustomerService")
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

            ga_service = client.get_service("GoogleAdsService")
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
                        child_accounts = await get_child_accounts(client, customer_id)
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
    except Exception as e:
        logging.error(f"Error listing customers: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error listing customers: {str(e)}"
        )


@app.get("/connector/google/auth")
async def auth_callback(request: Request, code: str = None, state: str = None):
    """Handle the OAuth callback from Google and return comprehensive account information"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    if not state or state not in flows:
        raise HTTPException(
            status_code=400, detail="Invalid or expired state parameter"
        )

    try:
        # Retrieve the flow object for this session
        flow = flows[state]

        # Pass the code back into the OAuth module to get a refresh token
        flow.fetch_token(code=code)
        refresh_token = flow.credentials.refresh_token

        # Clean up the flow object
        del flows[state]

        # Configure Google Ads client credentials
        credentials = {
            "refresh_token": refresh_token,
            "client_id": flow.credentials.client_id,
            "client_secret": flow.credentials.client_secret,
            "developer_token": "3WREvqoZUexzpH_oDUjOPw",
            "use_proto_plus": True,
        }

        # Initialize the Google Ads client
        client = GoogleAdsClient.load_from_dict(credentials)

        # Set date range (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        # Get both reports and customer list
        customers = await get_customer_list(client)
        campaign_reports = await get_google_ads_reports(client, start_date, end_date)

        auth_info = {
            "refresh_token": refresh_token,
            "access_token": flow.credentials.token,
            "token_expiry": (
                flow.credentials.expiry.isoformat() if flow.credentials.expiry else None
            ),  # Convert datetime to ISO format
            "token_uri": flow.credentials.token_uri,
            "client_id": flow.credentials.client_id,
            "client_secret": flow.credentials.client_secret,
            "scopes": list(flow.credentials.scopes),  # Convert set to list
        }

        response_data = {
            "auth_info": auth_info,
            "customers": {
                "total_customers": len(customers),
                "customer_list": customers,
            },
            "reports": {
                "date_range": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                },
                "campaigns": campaign_reports,
            },
        }

        # Log auth info and response data
        logging.info("Auth Info: %s", json.dumps(auth_info, indent=2))
        logging.info("Response Data: %s", json.dumps(response_data, indent=2))

        return response_data

    except Exception as e:
        logging.error("Error in auth_callback: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
