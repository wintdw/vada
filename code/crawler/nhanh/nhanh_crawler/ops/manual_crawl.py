import time
import requests
from datetime import datetime, timedelta

# Config
BASE_URL = (
    "http://localhost:8148/ingest/partner/nhanh/platform/crawl"  # update if needed
)
CRAWL_ID = "9eb69aa9-51bb-4931-9209-4f2e7d19ee6e"
# CRAWL_ID = "cfe2bf1a-b12e-48a2-a506-7d8de0c1f5e9"
DATE_FORMAT = "%Y-%m-%d"
REQUEST_DELAY = 1  # seconds

# Time range: from 2025-06-15 back to 2024-06-01
start_date = datetime(2025, 7, 31)
end_date = datetime(2025, 8, 4)
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
