import logging
from typing import Dict

from .request import tiktok_api_request


async def get_authorized_shops(access_token: str) -> Dict:
    """
    Fetch the shop info associated with the given access token.
    Merchant App only has one shop.
    """
    api_version = "202309"
    path = f"/authorization/{api_version}/shops"

    data = await tiktok_api_request(
        method="GET",
        path=path,
        access_token=access_token,
        shop_cipher="",  # Not required for this endpoint
    )
    logging.info(f"Getting authorized shops: {data}")

    shop_info = {}
    if "shops" in data:
        shop_info = data["shops"][0]  # For Merchant App: 1 shop only
        if len(data["shops"]) > 1:
            logging.warning(f"Multiple shops found: {len(data['shops'])}")
    else:
        logging.error(f"Error: {data}", exc_info=True)

    return shop_info


async def get_authorized_category_assets(access_token: str) -> Dict:
    """
    Fetch the authorized category assets for the shop associated with the given access token.
    """
    api_version = "202405"
    path = f"/authorization/{api_version}/category_assets"

    data = await tiktok_api_request(
        method="GET",
        path=path,
        access_token=access_token,
        shop_cipher="",  # Not required for this endpoint
    )
    logging.info(f"Getting authorized category assets: {data}")

    return data
