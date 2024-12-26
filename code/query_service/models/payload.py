from pydantic import BaseModel
from typing import List, Dict, Any

class Payload(BaseModel):
    agg_rule: Dict[Any, Any] | None = None
    aggregationSummary: List[Any] | None = None
    bucketResultFilters: List[Any] | None = None
    comparisons: List[Any] | None = None
    date_range: List[Any] | None = None
    formulars: List[Any] | None = None
    id: str | None = None
    index: str | None = None
    interval: str | None = None
    master_index: Dict[Any, Any] | None = None
    metadata: Dict[Any, Any] | None = None
    modifiedValues: List[Any] | None = None
    name: str | None = None
    operator_fields: List[Any] | None = None
    selectedDateRange: List[Any] | None = None
    shiftedDataVisibilities: Dict[Any, Any] | None = None
    modified_values: List[Any] | None = None
