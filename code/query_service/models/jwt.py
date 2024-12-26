from pydantic import BaseModel

class JWTPayload(BaseModel):
    name: str
    id: str
    exp: int | float
