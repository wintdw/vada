"""
Nhanh API service module for handling authentication and API interactions.

This module provides functions to interact with the Nhanh API, including
authentication via access tokens and other API operations.
"""

import aiohttp
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from tools.settings import settings


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
                    print(f"Error getting access token. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        print(f"HTTP client error while getting access token: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while getting access token: {e}")
        raise


async def get_product_categories(access_token: str) -> Optional[Dict]:
    """
    Get product categories from the Nhanh API.
    
    Args:
        access_token (str): The access token for authentication.
    
    Returns:
        Optional[Dict]: Product categories data or None if request fails.
    """
    url = "https://open.nhanh.vn/api/product/category"
    
    params = {
        "accessToken": access_token
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"Error getting product categories. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        print(f"HTTP client error while getting product categories: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while getting product categories: {e}")
        raise


async def get_products(access_token: str, page: int = 1, limit: int = 100) -> Optional[Dict]:
    """
    Get products from the Nhanh API.
    
    Args:
        access_token (str): The access token for authentication.
        page (int): Page number for pagination.
        limit (int): Number of products per page.
    
    Returns:
        Optional[Dict]: Products data or None if request fails.
    """
    url = "https://open.nhanh.vn/api/product/index"
    
    params = {
        "accessToken": access_token,
        "page": page,
        "limit": limit
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"Error getting products. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        print(f"HTTP client error while getting products: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while getting products: {e}")
        raise


async def get_staff(access_token: str) -> Optional[Dict]:
    """
    Get staff/users from the Nhanh API.
    
    Args:
        access_token (str): The access token for authentication.
    
    Returns:
        Optional[Dict]: Staff data or None if request fails.
    """
    url = "https://open.nhanh.vn/api/user/index"
    
    params = {
        "accessToken": access_token
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"Error getting staff. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        print(f"HTTP client error while getting staff: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while getting staff: {e}")
        raise


async def get_customers(access_token: str, page: int = 1, limit: int = 100, updated_at_from: str = None) -> Optional[Dict]:
    """
    Get customers from the Nhanh API.
    
    Args:
        access_token (str): The access token for authentication.
        page (int): Page number for pagination.
        limit (int): Number of customers per page.
        updated_at_from (str): Filter customers updated from this date (YYYY-MM-DD).
    
    Returns:
        Optional[Dict]: Customers data or None if request fails.
    """
    url = "https://open.nhanh.vn/api/customer/index"
    
    params = {
        "accessToken": access_token,
        "page": page,
        "limit": limit
    }
    
    if updated_at_from:
        params["updatedAtFrom"] = updated_at_from
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"Error getting customers. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        print(f"HTTP client error while getting customers: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while getting customers: {e}")
        raise


async def get_orders(access_token: str, from_date: str, to_date: str, page: int = 1, limit: int = 100) -> Optional[Dict]:
    """
    Get orders from the Nhanh API.
    
    Args:
        access_token (str): The access token for authentication.
        from_date (str): Start date for order filtering (YYYY-MM-DD).
        to_date (str): End date for order filtering (YYYY-MM-DD).
        page (int): Page number for pagination.
        limit (int): Number of orders per page.
    
    Returns:
        Optional[Dict]: Orders data or None if request fails.
    """
    url = "https://open.nhanh.vn/api/order/index"
    
    params = {
        "accessToken": access_token,
        "fromDate": from_date,
        "toDate": to_date,
        "page": page,
        "limit": limit
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"Error getting orders. Status: {response.status}, Response: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        print(f"HTTP client error while getting orders: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while getting orders: {e}")
        raise


async def crawl_nhanh_data(access_token: str, from_date: str = None, to_date: str = None) -> Dict:
    """
    Crawl all Nhanh data including categories, products, staff, customers, and orders.
    
    Args:
        access_token (str): The access token for authentication.
        from_date (str): Start date for order filtering (YYYY-MM-DD). Defaults to 30 days ago.
        to_date (str): End date for order filtering (YYYY-MM-DD). Defaults to today.
    
    Returns:
        Dict: Dictionary containing all crawled data and execution statistics.
    """
    start_time = datetime.now()
    
    # Set default dates if not provided
    if not from_date:
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
    
    result = {
        "execution_time": 0,
        "total_reports": 0,
        "data": {
            "categories": {},
            "products": {},
            "staff": {},
            "customers": {},
            "orders": {}
        },
        "errors": []
    }
    
    try:
        # Get product categories
        print("Fetching product categories...")
        categories_response = await get_product_categories(access_token)
        if categories_response and categories_response.get("data"):
            result["data"]["categories"] = categories_response["data"]
        
        # Get products (handle pagination)
        print("Fetching products...")
        page = 1
        while True:
            products_response = await get_products(access_token, page=page, limit=100)
            if products_response and products_response.get("data", {}).get("products"):
                products_data = products_response["data"]["products"]
                result["data"]["products"].update(products_data)
                
                # Check if there are more pages
                if len(products_data) < 100:
                    break
                page += 1
            else:
                break
        
        # Get staff
        print("Fetching staff...")
        staff_response = await get_staff(access_token)
        if staff_response and staff_response.get("data", {}).get("users"):
            result["data"]["staff"] = staff_response["data"]["users"]
        
        # Get customers (handle pagination)
        print("Fetching customers...")
        page = 1
        while True:
            customers_response = await get_customers(access_token, page=page, limit=100)
            if customers_response and customers_response.get("data", {}).get("customers"):
                customers_data = customers_response["data"]["customers"]
                result["data"]["customers"].update(customers_data)
                
                # Check if there are more pages
                if len(customers_data) < 100:
                    break
                page += 1
            else:
                break
        
        # Get orders - handle Nhanh's 10-day query limitation
        print("Fetching orders...")
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
        
        # Calculate the number of 10-day chunks needed
        current_date = from_date_obj
        while current_date <= to_date_obj:
            # Calculate end date for this chunk (max 10 days from current_date)
            chunk_end_date = min(current_date + timedelta(days=9), to_date_obj)
            
            chunk_from_date = current_date.strftime('%Y-%m-%d')
            chunk_to_date = chunk_end_date.strftime('%Y-%m-%d')
            
            print(f"Fetching orders from {chunk_from_date} to {chunk_to_date}")
            
            # Get orders for this date chunk (handle pagination)
            page = 1
            while True:
                orders_response = await get_orders(access_token, chunk_from_date, chunk_to_date, page=page, limit=100)
                if orders_response and orders_response.get("data", {}).get("orders"):
                    orders_data = orders_response["data"]["orders"]
                    result["data"]["orders"].update(orders_data)
                    
                    # Check if there are more pages
                    if len(orders_data) < 100:
                        break
                    page += 1
                else:
                    break
            
            # Move to next chunk
            current_date = chunk_end_date + timedelta(days=1)
        
        # Calculate totals
        result["total_reports"] = (
            len(result["data"]["categories"]) +
            len(result["data"]["products"]) +
            len(result["data"]["staff"]) +
            len(result["data"]["customers"]) +
            len(result["data"]["orders"])
        )
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"Error during Nhanh data crawling: {e}")
    
    finally:
        end_time = datetime.now()
        result["execution_time"] = (end_time - start_time).total_seconds()
    
    return result