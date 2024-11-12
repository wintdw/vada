from pydantic import BaseModel
from typing import Union


class JWTPayload(BaseModel):
    name: str
    id: str
    exp: Union[int, float]

    class Config:
        schema_extra = {
            "example": {
                "name": "user7500",
                "id": "65422b6aa2bbacc10b7a22a3",
                "exp": 1731306868,
            }
        }
