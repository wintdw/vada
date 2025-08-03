import json
import logging
from typing import Dict, List

from model.settings import settings
from .request import retry_post


async def get_products(business_id: str, access_token: str) -> List[Dict]:
    """
    Fetch all products for a given business.
    This function retrieves all products by paginating through the results.
    """
    url = f"{settings.NHANH_BASE_URL}/product/search"
    products = []
    page = 1

    logging.info(f"[{business_id}] Fetching products...")
    while True:
        payload = {"page": page}
        response_data = await retry_post(
            url=url,
            business_id=business_id,
            access_token=access_token,
            payload=json.dumps(payload),
        )

        if not response_data:
            break

        page_products = response_data.get("products", {})
        products.extend(page_products.values())

        current_page = response_data.get("currentPage", page)
        total_pages = response_data.get("totalPages", current_page)

        if current_page >= total_pages:
            break

        page += 1

    logging.info(f"[{business_id}] Total products fetched: {len(products)}")

    return products


async def get_product_detail(
    business_id: str,
    access_token: str,
    product_id: str,
) -> Dict:
    url = f"{settings.NHANH_BASE_URL}/product/detail"
    product_detail = await retry_post(
        url=url,
        business_id=business_id,
        access_token=access_token,
        payload=product_id,
    )

    return product_detail
