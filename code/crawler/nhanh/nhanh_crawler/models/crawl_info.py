from pydantic import BaseModel
from datetime import datetime

class NhanhCrawlInfo(BaseModel):
    index_name: str
    business_id: str
    access_token: str
    depot_ids: list[str]
    expired_datetime: datetime
    crawl_interval: int = 20
    last_crawl_time: datetime | None = None
    next_crawl_time: datetime | None = None

class NhanhCrawlInfoResponse(BaseModel):
    status: int
    message: str
    data: list[NhanhCrawlInfo] | NhanhCrawlInfo | None = None
