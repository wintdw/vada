from typing import Optional
from pydantic import BaseModel  # type: ignore


class UsersRequest(BaseModel):
    user_email: str
    user_name: str
    user_passwd: str
