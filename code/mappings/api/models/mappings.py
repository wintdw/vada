from typing import Dict, Optional
from pydantic import BaseModel  # type: ignore


class MasterIndex(BaseModel):
    name: str
    friendly_name: str
    agg_field: str
    id_field: str
    time_field: str
    mappings: Dict


class CopyMappingsRequest(BaseModel):
    user_id: str
    index_name: str
    index_friendly_name: Optional[str] = None


class SetMappingsRequest(BaseModel):
    index_name: str
    mappings: Dict
