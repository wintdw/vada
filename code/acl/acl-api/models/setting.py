from __future__ import annotations
from pydantic import BaseModel

class NotReadable(BaseModel):
    field: str

class Operator(BaseModel):
    field: str
    metric: str

class Rule(BaseModel):
    field: str
    id: str
    operator: str
    type: str
    input: str
    value: list[str | int] | list[list[str | int]] | str | int

class Filter(BaseModel):
    condition: str = "AND"
    rules: list[Rule | Filter] = []

    def simplify(self) -> Filter:
        simplified_rules = [rule.simplify() if isinstance(rule, Filter) else rule for rule in self.rules]
        if len(simplified_rules) == 1 and isinstance(simplified_rules[0], Filter):
            return simplified_rules[0]
        else:
            self.rules = simplified_rules
            return self

class Permission(BaseModel):
    index_name: str
    not_readables: list[NotReadable] = []
    permit_filter: Filter
    permit_operators: list[Operator] = []

    def clean(self):
        if self.permit_filter:
            self.permit_filter = self.permit_filter.simplify()

class Setting(BaseModel):
    permissions: list[Permission] | Permission = []
