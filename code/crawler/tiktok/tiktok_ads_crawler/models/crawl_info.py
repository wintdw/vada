from pydantic import BaseModel
from datetime import datetime

class CrawlInfo(BaseModel):
    crawl_id: str | None = None
    index_name: str
    crawl_type: str
    access_token: str
    refresh_token: str = ""
    access_token_updated_at: datetime | None = None
    crawl_interval: int = 1440
    crawl_from_date: datetime 
    crawl_to_date: datetime 
    last_crawl_time: datetime | None = None
    next_crawl_time: datetime | None = None

class CrawlInfoResponse(BaseModel):
    status: int
    message: str
    data: list[CrawlInfo] | CrawlInfo | None = None
