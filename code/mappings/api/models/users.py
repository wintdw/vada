from pydantic import BaseModel


class UsersRequest(BaseModel):
    email: str
    user: str
    passwd: str
    index: str
