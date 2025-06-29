from pydantic import BaseModel

class UserGroup(BaseModel):
    user_id: str
    group_id: str

class UserGroupResponse(BaseModel):
    status: int
    message: str
    data: list[UserGroup] | UserGroup = []
