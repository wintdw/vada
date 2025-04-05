from pydantic import BaseModel

class Advertiser(BaseModel):
  advertiser_id: str
  advertiser_name: str

class AdvertiserInfo(BaseModel):
  rejection_reason: str | None
  license_no: str
  timezone: str
  brand: str | None
  promotion_center_city: str | None
  contacter: str
  status: str
  industry: str
  currency: str
  country: str
  create_time: int
  telephone_number: str
  company: str
  address: str | None
  license_city: str | None
  language: str
  license_url: str | None
  advertiser_account_type: str
  license_province: str | None
  balance: int
  cellphone_number: str
  promotion_center_province: str | None
  role: str
  advertiser_id: str
  description: str
  name: str
  email: str
  promotion_area: str
  display_timezone: str

class PageInfo(BaseModel):
    page: int
    page_size: int
    total_page: int
    total_number: int

class ReportIntegrated(BaseModel):
  nothing: None = None 

class DataPayload(BaseModel):
  list: list[Advertiser | AdvertiserInfo | ReportIntegrated]
  page_info: PageInfo = None

class TiktokBusinessResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: DataPayload | None
