from pydantic import BaseModel  # type: ignore
from datetime import datetime


class CrawlHistory(BaseModel):
    history_id: str | None = None
    crawl_id: str | None = None
    crawl_time: datetime | None = None
    crawl_status: str = "in_progress"
    crawl_error: str = ""
    crawl_duration: int = 0
    crawl_data_number: int = 0


class CrawlHistoryResponse(BaseModel):
    status: int
    message: str
    data: list[CrawlHistory] | CrawlHistory | None = None
