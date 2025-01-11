from typing import Optional
from pydantic import BaseModel  # type: ignore


class UsersRequest(BaseModel):
    user_email: str
    user_name: str
    user_passwd: str
    index_name: str
    index_friendly_name: Optional[str] = None
