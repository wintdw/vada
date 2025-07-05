"""
Nhanh API service module for handling authentication and API interactions.

This module provides functions to interact with the Nhanh API, including
authentication via access tokens and other API operations.
"""

import aiohttp
import os
from typing import Dict, Optional

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