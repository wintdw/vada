from typing import Dict, List, Any
from pydantic import BaseModel  # type: ignore


##### NEW FORMAT
class InsertRequest(BaseModel):
    meta: Dict[str, str]
    data: List[Dict[str, Any]]
