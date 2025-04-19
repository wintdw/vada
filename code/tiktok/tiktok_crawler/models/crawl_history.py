from pydantic import BaseModel
from datetime import datetime

class CrawlHistory(BaseModel):
    crawl_id: str | None = None
    crawl_time: datetime = datetime.now()
    crawl_status: str
    crawl_error: str
    crawl_duration: int
    crawl_data_number: int

class CrawlHistoryResponse(BaseModel):
    status: int
    message: str
    data: list[CrawlHistory] | CrawlHistory = []
