"""
Nhanh API service module for handling authentication and API interactions.

This module provides functions to interact with the Nhanh API, including
authentication via access tokens and other API operations.
"""

import aiohttp
import os
import json
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from tools.settings import settings
from tools import get_logger

logger = get_logger(__name__, 10)

async def get_access_token(access_code: str) -> Optional[Dict]:
    """
    Get an access token from the Nhanh API using the provided access code.
    
    Makes a POST request to the Nhanh OAuth endpoint to exchange the access code
    for an access token. This is typically the first step in the OAuth flow
    after receiving an access code from the user authorization.
    
    The function reads appId, version, and secretKey from the application settings
    and only requires the access_code as input parameter.
    
    Args:
        access_code (str): The access code received from the OAuth authorization.
    
    Returns:
        Optional[Dict]: A dictionary containing the API response with the access token
                       and other OAuth information. Returns None if the request fails.
    
    Raises:
        aiohttp.ClientError: If there's an error with the HTTP request.
        Exception: For other unexpected errors during the API call.
        ValueError: If required settings are not configured.
        
    Note:
        The API requires appId, version, secretKey, and accessCode parameters as indicated
        by the API documentation at https://open.nhanh.vn/api/oauth/access_token
    """
    url = "https://open.nhanh.vn/api/oauth/access_token"
    
    # Read settings
    app_id = settings.NHANH_APP_ID
    version = settings.NHANH_OAUTH_VERSION
    secret_key_file = settings.NHANH_SECRET_KEY_FILE
    
    # Validate required settings
    if not app_id:
        raise ValueError("NHANH_APP_ID is not configured in settings")
    if not version:
        raise ValueError("NHANH_OAUTH_VERSION is not configured in settings")
    if not secret_key_file:
        raise ValueError("NHANH_SECRET_KEY_FILE is not configured in settings")
    
    # Read secret key from file
    if not os.path.isfile(secret_key_file):
        raise ValueError(f"Secret key file not found: {secret_key_file}")
    
    with open(secret_key_file, "r") as f:
        secret_key = f.read().strip()
    
    # Prepare the request payload
    payload = {
        "appId": app_id,
        "version": version,
        "secretKey": secret_key,
        "accessCode": access_code
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    # Log the error response for debugging
                    error_text = await response.text()
                    logger.debug(f"Error getting access token. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.debug(f"HTTP client error while getting access token: {e}")
        raise
    except Exception as e:
        logger.debug(f"Unexpected error while getting access token: {e}")
        raise

async def get_product_detail(business_id: str, access_token: str, product_id: str, ) -> Dict:
    """
    Get detailed information about a product from the Nhanh API.
    This function retrieves product details using the product ID, business ID,
    and access token.
    Args:
        product_id (str): The ID of the product to retrieve.
        business_id (str): The ID of the business associated with the product.
        access_token (str): The access token for authentication.
    Returns:
        Dict: A dictionary containing the product details. If the request fails,
              an empty dictionary is returned.
    Raises:
        aiohttp.ClientError: If there's an error with the HTTP request.
        Exception: For other unexpected errors during the API call.
    """
    url = "https://open.nhanh.vn/api/product/detail"

    headers = {
        "Accept": "application/json"
    }
    payload = {
        "version": settings.NHANH_OAUTH_VERSION,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
        "data": str(product_id)
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {})
                else:
                    error_text = await response.text()
                    logger.debug(f"Error getting product detail. Status: {response.status}, Response: {error_text}")
                    return {}
    except aiohttp.ClientError as e:
        logger.debug(f"HTTP client error while getting product detail: {e}")
        raise
    except Exception as e:
        logger.debug(f"Unexpected error while getting product detail: {e}")
        raise

async def get_orders(business_id: str, access_token: str, from_date: str, to_date: str, page: int = 1):
    """
    Get a list of orders from the Nhanh API within the specified date range.

    This function retrieves orders using the provided from_date and to_date
    parameters, and returns the order data if the request is successful.

    Args:
        business_id (str): The ID of the business.
        access_token (str): The access token for authentication.
        from_date (str): The start date for the order retrieval in ISO format.
        to_date (str): The end date for the order retrieval in ISO format.
        page (int): The page number for pagination (default is 1).

    Returns:
        dict: A dictionary containing the order data. If the request fails,
              an empty dictionary is returned.

    Raises:
        aiohttp.ClientError: If there's an error with the HTTP request.
        Exception: For other unexpected errors during the API call.
    """
    url = "https://open.nhanh.vn/api/order/index"
    headers = {
        "Accept": "application/json"
    }
    payload = {
        "fromDate": from_date,
        "toDate": to_date,
        "page": page
    }
    data = {
        "version": settings.NHANH_OAUTH_VERSION,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
        "data": json.dumps(payload)
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {})
                else:
                    error_text = await response.text()
                    logger.debug(f"Error getting orders. Status: {response.status}, Response: {error_text}")
                    return {}
    except aiohttp.ClientError as e:
        logger.debug(f"HTTP client error while getting orders: {e}")
        raise
    except Exception as e:
        logger.debug(f"Unexpected error while getting orders: {e}")
        raise

async def crawl_nhanh_data(business_id: str, access_token: str, from_date: str, to_date: str) -> List[Dict]:
    """
    Crawl data from Nhanh API by retrieving orders and their corresponding product details.

    Args:
        business_id (str): The ID of the business.
        access_token (str): The access token for authentication.
        from_date (str): The start date for the order retrieval in ISO format.
        to_date (str): The end date for the order retrieval in ISO format.

    Returns:
        List[Dict]: A list of dictionaries containing order and product details.
    """
    try:
        detailed_data = []
        total_pages = 1
        page = 1

        while page <= total_pages:
            logger.debug(f"Fetching page {page} for orders from {from_date} to {to_date}")
            # Get orders for the current page
            data = await get_orders(business_id, access_token, from_date, to_date, page)

            total_pages = data.get("totalPages", 1)
            orders = data.get("orders", {})

            # Iterate through orders and fetch product details
            for order_id, order in orders.items():
                for product in order.get("products", []):
                    product_id = product.get("productId")
                    if product_id:
                        product["detail"] = await get_product_detail(business_id, access_token, product_id)
                        time.sleep(0.05)  # avoid API overuse               
                detailed_data.append(order)
            page += 1

        return detailed_data

    except Exception as e:
        logger.debug(f"Error while crawling Nhanh data: {e}")
        raise