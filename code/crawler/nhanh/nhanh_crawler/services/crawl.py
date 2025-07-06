import aiohttp
import asyncio
import json
import argparse
from datetime import datetime, timedelta

# --- Configuration Variables ---
app_id = "75154"
business_id = "108233"
access_token = ""
BATCH_SIZE = 1000
index_name = "ducnc_test_nhanh"
# -------------------------------

ORDER_API_URL = "https://open.nhanh.vn/api/order/index"
PRODUCT_DETAIL_API_URL = "https://open.nhanh.vn/api/product/detail"
INSERT_API_URL = "http://insert-dev.internal.vadata.vn/json"

headers = {
    "Accept": "application/json"
}

async def get_product_detail(session, product_id):
    async with session.post(
        PRODUCT_DETAIL_API_URL,
        headers=headers,
        data={
            'version': '2.0',
            'appId': app_id,
            'businessId': business_id,
            'accessToken': access_token,
            'data': str(product_id)
        }
    ) as response:
        if response.status == 200:
            res_json = await response.json()
            return res_json.get("data", {})
        return {}

def enrich_report(report: dict, index_name: str, doc_id: str) -> dict:
    metadata = {
        "_vada": {
            "ingest": {
                "destination": {"type": "elasticsearch", "index": index_name},
                "vada_client_id": "a_quang_nguyen",
                "doc_id": doc_id,
            }
        }
    }
    return report | metadata

async def enrich_order(session, order):
    try:
        timestamp = int(datetime.strptime(order["createdDateTime"], "%Y-%m-%d %H:%M:%S").timestamp())
    except Exception as e:
        print(f"❌ Invalid createdDateTime for order {order.get('id')}: {e}")
        timestamp = 0

    for product in order.get("products", []):
        product_id = product.get("productId")
        if product_id:
            product["detail"] = await get_product_detail(session, product_id)
            await asyncio.sleep(0.05)  # Avoid API overuse

    doc_id = f"{order['id']}_{timestamp}"
    return enrich_report(order, index_name, doc_id)

async def send_batch(session, batch):
    payload = {
        "meta": {"index_name": index_name},
        "data": batch
    }
    try:
        async with session.post(INSERT_API_URL, json=payload) as response:
            if response.status == 200:
                print(f"✅ Sent batch of {len(batch)}")
            else:
                text = await response.text()
                print(f"❌ Failed to send batch: {response.status}, {text}")
    except Exception as e:
        print(f"❌ Exception during sending: {e}")

async def fetch_and_push_all_orders(from_date: str, to_date: str):
    async with aiohttp.ClientSession() as session:
        page = 1
        total_pages = 1
        batch = []
        total_orders = 0

        while page <= total_pages:
            print(f"Fetching page {page}")
            payload = {
                "fromDate": from_date,
                "toDate": to_date,
                "page": page
            }

            async with session.post(
                ORDER_API_URL,
                headers=headers,
                data={
                    'version': '2.0',
                    'appId': app_id,
                    'businessId': business_id,
                    'accessToken': access_token,
                    'data': json.dumps(payload)
                }
            ) as response:
                if response.status != 200:
                    print(f"❌ Request failed: {response.status}")
                    break

                res_json = await response.json()
                if res_json.get("code") != 1:
                    print(f"❌ API error: {res_json.get('message')}")
                    print(f"{res_json}")
                    break

                data = res_json.get("data", {})
                total_pages = data.get("totalPages", 1)
                orders = data.get("orders", {})

                for order_id, order in orders.items():
                    enriched = await enrich_order(session, order)
                    batch.append(enriched)
                    total_orders += 1

                    if len(batch) >= BATCH_SIZE:
                        await send_batch(session, batch)
                        batch = []

                page += 1

        if batch:
            await send_batch(session, batch)

        print(f"✅ Done. Total orders pushed: {total_orders}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and push orders from Nhanh.vn.")
    args = parser.parse_args()

    today = datetime.today().date()
    from_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    asyncio.run(fetch_and_push_all_orders(from_date, to_date))