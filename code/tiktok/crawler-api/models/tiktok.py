from pydantic import BaseModel

class Tiktok(BaseModel):
    access_token: str
    app_id: str
    secret: str
