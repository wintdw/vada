from datetime import datetime
from prometheus_client import Gauge  # type: ignore

from model.setting import settings
from .mysql import get_crawl_info

# Define Prometheus Gauges
ggad_last_crawl_time = Gauge(
    "ggad_last_crawl_time", "Last crawl time (epoch seconds)", ["crawl_id", "app_env"]
)
ggad_next_crawl_time = Gauge(
    "ggad_next_crawl_time", "Next crawl time (epoch seconds)", ["crawl_id", "app_env"]
)


async def update_crawl_metrics():
    infos = await get_crawl_info()
    for info in infos:
        crawl_id = info.get("crawl_id")
        last_crawl_time = info.get("last_crawl_time")
        next_crawl_time = info.get("next_crawl_time")
        # Convert ISO8601 to epoch seconds if present
        if last_crawl_time:
            dt = datetime.fromisoformat(last_crawl_time)
            ggad_last_crawl_time.labels(
                crawl_id=crawl_id, app_env=settings.APP_ENV
            ).set(dt.timestamp())
        if next_crawl_time:
            dt = datetime.fromisoformat(next_crawl_time)
            ggad_next_crawl_time.labels(
                crawl_id=crawl_id, app_env=settings.APP_ENV
            ).set(dt.timestamp())
