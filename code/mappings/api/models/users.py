from pydantic import BaseModel  # type: ignore


class UsersRequest(BaseModel):
    email: str
    user: str
    passwd: str
    index: str
