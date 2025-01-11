from pydantic import BaseModel  # type: ignore


class JWTPayload(BaseModel):
    name: str
    id: str
    exp: int
