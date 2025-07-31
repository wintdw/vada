import time
import requests
from datetime import datetime, timedelta

# Config
BASE_URL = "http://localhost:8148/ingest/partner/tiktok/shop/crawl"  # update if needed
CRAWL_ID = "091f89ae-4ba8-4cc0-98a8-7201b85b815e"
DATE_FORMAT = "%Y-%m-%d"
REQUEST_DELAY = 1  # seconds

# Time range: from 2025-06-15 back to 2024-06-01
start_date = datetime(2024, 6, 1)
end_date = datetime(2025, 6, 15)
delta = timedelta(days=1)

current_day = end_date

while current_day > start_date:
    previous_day = current_day - delta

    params = {
        "crawl_id": CRAWL_ID,
        "start_date": previous_day.strftime(DATE_FORMAT),
        "end_date": current_day.strftime(DATE_FORMAT),
    }

    print("=" * 60)
    print(f"Triggering crawl for range: {params['start_date']} → {params['end_date']}")
    print(
        f"Sending request to: {BASE_URL}?crawl_id={CRAWL_ID}&start_date={params['start_date']}&end_date={params['end_date']}"
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
