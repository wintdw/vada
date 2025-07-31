import aiohttp  # type: ignore
import logging
from typing import Dict

from model.settings import settings


async def get_access_token(access_code: str) -> Dict:
    """
    API documentation at https://open.nhanh.vn/api/oauth/access_token
    """
    url = f"{settings.NHANH_BASE_URL}/oauth/access_token"
    oauth_version = "2.0"
    app_id = settings.NHANH_APP_ID
    secret_key = settings.NHANH_SECRET_KEY

    # Prepare the request payload
    payload = {
        "appId": app_id,
        "version": oauth_version,
        "secretKey": secret_key,
        "accessCode": access_code,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logging.debug(
                        f"Error getting access token. Status: {response.status}, Response: {await response.text()}",
                        exc_info=True,
                    )
                    return {}

    except Exception as e:
        logging.debug(
            f"Unexpected error while getting access token: {e}", exc_info=True
        )
        raise
