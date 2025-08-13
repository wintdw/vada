from datetime import datetime
from prometheus_client import Gauge, Counter  # type: ignore

from model.settings import settings
from .crawl_info import get_crawl_info


# Define Prometheus Gauges
last_crawl_time_gauge = Gauge(
    "nhanh_last_crawl_time",
    "Last crawl time (epoch seconds)",
    ["crawl_id", "app_env"],
)
next_crawl_time_gauge = Gauge(
    "nhanh_next_crawl_time",
    "Next crawl time (epoch seconds)",
    ["crawl_id", "app_env"],
)
crawl_info_gauge = Gauge(
    "nhanh_crawl_info",
    "Crawl info for Nhanh",
    [
        "crawl_id",
        "business_id",
        "account_id",
        "vada_uid",
        "index_name",
        "app_env",
    ],
)
access_token_expiry_gauge = Gauge(
    "nhanh_access_token_expiry",
    "Access token expiry for Nhanh",
    ["crawl_id", "app_env"],
)
insert_success_counter = Counter(
    "nhanh_insert_success",
    "Number of successfully persisted docs",
    ["crawl_id", "app_env"],
)
insert_failure_counter = Counter(
    "nhanh_insert_failure",
    "Number of failed docs to persist",
    ["crawl_id", "app_env"],
)


async def update_crawl_metrics():
    infos = await get_crawl_info()
    for info in infos:
        crawl_id = info.get("crawl_id")
        business_id = info.get("business_id")
        account_id = info.get("account_id")
        vada_uid = info.get("vada_uid")
        index_name = info.get("index_name")
        last_crawl_time = info.get("last_crawl_time")
        next_crawl_time = info.get("next_crawl_time")
        expired_datetime = info.get("expired_datetime")

        # Set crawl_info_gauge to 1 for each crawl_id (can be used for label-only metrics)
        crawl_info_gauge.labels(
            crawl_id=crawl_id,
            business_id=business_id,
            account_id=account_id,
            vada_uid=vada_uid,
            index_name=index_name,
            app_env=settings.APP_ENV,
        ).set(1)

        # Set token_expiry_gauge to expiry timestamp for each crawl_id
        if expired_datetime:
            dt = datetime.fromisoformat(expired_datetime)
            access_token_expiry_gauge.labels(
                crawl_id=crawl_id, app_env=settings.APP_ENV
            ).set(dt.timestamp())

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
