from typing import Dict, Optional
from pydantic import BaseModel  # type: ignore


class MasterIndex(BaseModel):
    name: str
    friendly_name: str
    agg_field: str
    id_field: str
    time_field: str
    mappings: Dict


class MappingsRequest(BaseModel):
    user_id: str
    index_name: str
    index_friendly_name: Optional[str] = None
