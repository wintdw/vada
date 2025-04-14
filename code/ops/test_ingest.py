import asyncio
import aiohttp  # type: ignore
import json


async def test_ingest():
    # Sample data matching the expected format
    payload = {
        "meta": {
            "user_id": "test_user_123",
            "index_name": "test_index",
            "index_friendly_name": "Test Index",
        },
        "data": [
            {"id": "1", "name": "Product A", "price": 100.50, "quantity": 50},
            {"id": "2", "name": "Product B", "price": 75.25, "quantity": 30},
        ],
    }

    # API endpoint
    url = "http://ingest-dev.internal.vadata.vn/v1/json"

    # Send request
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            # Print status and response
            print(f"Status: {response.status}")
            result = await response.json()
            print("Response:", json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_ingest())
