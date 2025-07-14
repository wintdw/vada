from pydantic import BaseModel
from datetime import datetime

class NhanhCrawlHistory(BaseModel):
    history_id: str | None = None
    business_id: str
    crawl_time: datetime | None = None
    crawl_status: str = "in_progress"
    crawl_error: str = ""
    crawl_duration: int = 0
    crawl_data_number: int = 0

class NhanhCrawlHistoryResponse(BaseModel):
    status: int
    message: str
    data: list[NhanhCrawlHistory] | NhanhCrawlHistory | None = None
