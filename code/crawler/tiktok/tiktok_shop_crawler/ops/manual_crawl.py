import time
import requests
from datetime import datetime, timedelta

# Config
BASE_URL = "http://localhost:8148/ingest/partner/tiktok/shop/crawl"
CRAWL_IDS = [
    "091f89ae-4ba8-4cc0-98a8-7201b85b815e",
    "3f324f08-bc54-4ab6-b90f-b6ed11a1ea9e",
    "bd32c8f1-4316-4ca0-9e9c-d7470abefae5",
]  # Add as many as you want
DATE_FORMAT = "%Y-%m-%d"
REQUEST_DELAY = 1  # seconds

# Time range
start_date = datetime(2025, 7, 31)
end_date = datetime(2025, 8, 4)
delta = timedelta(days=1)

current_day = end_date

while current_day > start_date:
    previous_day = current_day - delta

    for crawl_id in CRAWL_IDS:
        params = {
            "crawl_id": crawl_id,
            "start_date": previous_day.strftime(DATE_FORMAT),
            "end_date": current_day.strftime(DATE_FORMAT),
        }

        print("=" * 60)
        print(
            f"Triggering crawl {crawl_id} for range: {params['start_date']} → {params['end_date']}"
        )
        print(
            f"Sending request to: {BASE_URL}?crawl_id={crawl_id}&start_date={params['start_date']}&end_date={params['end_date']}"
        )

        try:
            response = requests.get(BASE_URL, params=params)
            print(f"Response Status: {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except Exception:
                print("Response content:", response.text)
        except Exception as e:
            print(f"Error during request: {e}")

        print("Waiting before next request...\n")
        time.sleep(REQUEST_DELAY)

    current_day = previous_day
