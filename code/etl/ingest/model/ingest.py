from typing import List, Dict, Optional
from pydantic import BaseModel  # type: ignore


class MetaData(BaseModel):
    index_name: str
    index_friendly_name: Optional[str] = None
    user_id: str


class IngestRequest(BaseModel):
    meta: MetaData
    data: List[Dict]
