from typing import Dict
from pydantic import BaseModel


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
