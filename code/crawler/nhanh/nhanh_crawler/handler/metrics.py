from datetime import datetime
from prometheus_client import Gauge  # type: ignore
from fastapi import APIRouter  # type: ignore

from .crawl_info import get_crawl_info

router = APIRouter()

# Define Prometheus Gauges
last_crawl_time_gauge = Gauge(
    "nhanh_last_crawl_time", "Last crawl time (epoch seconds)", ["crawl_id"]
)
next_crawl_time_gauge = Gauge(
    "nhanh_next_crawl_time", "Next crawl time (epoch seconds)", ["crawl_id"]
)


async def update_crawl_metrics():
    infos = await get_crawl_info()
    for info in infos:
        crawl_id = info.get("crawl_id")
        last_crawl_time = info.get("last_crawl_time")
        next_crawl_time = info.get("next_crawl_time")
        # Convert ISO8601 to epoch seconds if present
        if last_crawl_time:
            try:
                dt = datetime.fromisoformat(last_crawl_time)
                last_crawl_time_gauge.labels(crawl_id=crawl_id).set(dt.timestamp())
            except Exception:
                pass
        if next_crawl_time:
            try:
                dt = datetime.fromisoformat(next_crawl_time)
                next_crawl_time_gauge.labels(crawl_id=crawl_id).set(dt.timestamp())
            except Exception:
                pass
