from pydantic import BaseModel

class Advertiser(BaseModel):
  advertiser_id: str
  advertiser_name: str

class AdvertiserList(BaseModel):
  list: list[Advertiser]

class AdvertiserResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: AdvertiserList
