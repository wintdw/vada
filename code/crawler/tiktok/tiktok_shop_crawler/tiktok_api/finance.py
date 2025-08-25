from typing import Dict

from .request import tiktok_api_request


async def get_transactions_by_order(
    access_token: str,
    shop_cipher: str,
    order_id: str,
) -> Dict:
    """
    Get Transactions by Order.
    Required scope: seller.finance.info

    Uses helper tiktok_api_request (same style as order_api) to call:
    GET /finance/202501/orders/{order_id}/statement_transactions

    - access_token: seller access token (x-tts-access-token)
    - shop_cipher: shop cipher from Get Authorization Shop
    - order_id: TikTok order id
    """
    api_version = "202501"
    path = f"/finance/{api_version}/orders/{order_id}/statement_transactions"

    data = await tiktok_api_request(
        method="GET", path=path, access_token=access_token, shop_cipher=shop_cipher
    )

    return data
