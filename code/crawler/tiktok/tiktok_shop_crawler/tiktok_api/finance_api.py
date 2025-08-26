import logging
from typing import Dict, List, Any

from .request import tiktok_api_request


async def get_statements(
    access_token: str, shop_cipher: str, statement_time_ge: int, statement_time_lt: int
) -> Dict[str, Any]:
    """
    Fetch statements from TikTok Shop API (paginated) — mimics list_order style.

    Args:
      access_token: seller access token
      shop_cipher: shop cipher
      statement_time_ge: inclusive lower bound (epoch seconds)
      statement_time_lt: exclusive upper bound (epoch seconds)

    Returns:
      Dict with keys: "total" and "statements" aggregated across pages.
    """
    api_version = "202309"
    path = f"/finance/{api_version}/statements"

    all_statements: List[Dict] = []
    page_token: str = ""

    while True:
        query_params = {
            "page_size": 100,
            "sort_field": "statement_time",
        }
        if page_token:
            query_params["page_token"] = page_token

        # add time filters and optional status as query params
        query_params["statement_time_ge"] = statement_time_ge
        query_params["statement_time_lt"] = statement_time_lt

        data = await tiktok_api_request(
            method="GET",
            path=path,
            access_token=access_token,
            shop_cipher=shop_cipher,
            params=query_params,
        )

        statements = data.get("statements", [])
        if not statements:
            break

        all_statements.extend(statements)

        page_token = data.get("next_page_token", "")
        if page_token:
            logging.info(f"More statements available, next page_token: {page_token}")
        else:
            logging.info("No more statements available")
            break

    return {"total": len(all_statements), "statements": all_statements}


async def get_transactions_by_statement(
    access_token: str,
    shop_cipher: str,
    statement_id: str,
) -> Dict:
    """
    Fetch all transactions for a statement (handles paging internally).

    Calls: GET /finance/202501/statements/{statement_id}/statement_transactions

    Returns {"total": n, "transactions": [...]} aggregated across pages.
    """
    api_version = "202501"
    path = f"/finance/{api_version}/statements/{statement_id}/statement_transactions"

    all_transactions: List[Dict] = []
    page_token: str = ""

    while True:
        params = {
            "page_size": 100,
            "sort_field": "order_create_time",
        }
        if page_token:
            params["page_token"] = page_token

        data = await tiktok_api_request(
            method="GET",
            path=path,
            access_token=access_token,
            shop_cipher=shop_cipher,
            params=params,
        )

        logging.debug(f"Fetched transactions page for statement {statement_id}: {data}")

        transactions = data.get("transactions", [])

        if not transactions:
            break

        all_transactions.extend(transactions)

        page_token = data.get("next_page_token", "")
        if page_token:
            logging.info(f"More transactions available, next page_token: {page_token}")
        else:
            logging.debug("No more transactions available")
            break

    return {"total": len(all_transactions), "transactions": all_transactions}


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

    logging.debug(f"Fetched transaction detail for order {order_id}: {data}")

    return data
