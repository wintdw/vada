from pydantic import BaseModel, validator
from datetime import datetime
import json

class NhanhCrawlInfo(BaseModel):
    index_name: str
    business_id: int
    access_token: str
    depot_ids: list[str]
    expired_datetime: datetime
    crawl_interval: int = 120
    last_crawl_time: datetime | None = None
    next_crawl_time: datetime | None = None

    @validator('depot_ids', pre=True)
    def parse_depot_ids(cls, v):
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON for depot_ids")
        if not isinstance(v, list):
            raise ValueError("depot_ids must be a list")
        # Ensure all items are strings
        return [str(item) for item in v]

class NhanhCrawlInfoResponse(BaseModel):
    status: int
    message: str
    data: list[NhanhCrawlInfo] | NhanhCrawlInfo | None = None
