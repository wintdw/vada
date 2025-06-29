from pydantic import BaseModel

class Group(BaseModel):
    group_id: str | None = None
    name: str
    description: str = ""
    priority: int = 100

class GroupResponse(BaseModel):
    status: int
    message: str
    data: list[Group] | Group = []
