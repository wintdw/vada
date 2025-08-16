from datetime import datetime
from prometheus_client import Gauge, Counter  # type: ignore

from model.settings import settings
from .crawl_info import get_crawl_info


# Define Prometheus Gauges
last_crawl_time_gauge = Gauge(
    "ppc_last_crawl_time",
    "Last crawl time (epoch seconds)",
    ["crawl_id", "app_env"],
)
next_crawl_time_gauge = Gauge(
    "ppc_next_crawl_time",
    "Next crawl time (epoch seconds)",
    ["crawl_id", "app_env"],
)
crawl_info_gauge = Gauge(
    "ppc_crawl_info",
    "Crawl info for PPC",
    [
        "crawl_id",
        "vada_uid",
        "index_name",
        "app_env",
    ],
)
insert_success_counter = Counter(
    "ppc_insert_success",
    "Number of successfully persisted docs",
    ["crawl_id", "app_env"],
)
insert_failure_counter = Counter(
    "ppc_insert_failure",
    "Number of failed docs to persist",
    ["crawl_id", "app_env"],
)


async def update_crawl_metrics():
    infos = await get_crawl_info()
    for info in infos:
        crawl_id = info.get("crawl_id")
        vada_uid = info.get("vada_uid")
        index_name = info.get("index_name")
        last_crawl_time = info.get("last_crawl_time")
        next_crawl_time = info.get("next_crawl_time")

        # Set crawl_info_gauge to 1 for each crawl_id (can be used for label-only metrics)
        crawl_info_gauge.labels(
            crawl_id=crawl_id,
            vada_uid=vada_uid,
            index_name=index_name,
            app_env=settings.APP_ENV,
        ).set(1)

        # Convert ISO8601 to epoch seconds if present
        if last_crawl_time:
            dt = datetime.fromisoformat(last_crawl_time)
            last_crawl_time_gauge.labels(
                crawl_id=crawl_id, app_env=settings.APP_ENV
            ).set(dt.timestamp())
        if next_crawl_time:
            dt = datetime.fromisoformat(next_crawl_time)
            next_crawl_time_gauge.labels(
                crawl_id=crawl_id, app_env=settings.APP_ENV
            ).set(dt.timestamp())
