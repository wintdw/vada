from pydantic import BaseModel

class PageInfo(BaseModel):
  page: int
  page_size: int
  total_page: int
  total_number: int

class AdGroup(BaseModel):
  adgroup_id: str
  campaign_id: str
  advertiser_id: str

class AdGroupPayload(BaseModel):
  list: list[AdGroup]
  page_info: PageInfo 

class AdGroupResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: AdGroupPayload 

class Campaign(BaseModel):
  campaign_id: str
  advertiser_id: str

class CampaignPayload(BaseModel):
  list: list[Campaign]
  page_info: PageInfo 

class CampaignResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: CampaignPayload 

class Ad(BaseModel):
  ad_id: str
  advertiser_id: str
  adgroup_id: str
  campaign_id: str

class AdPayload(BaseModel):
  list: list[Ad]
  page_info: PageInfo 

class AdResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: AdPayload 

class Dimensions(BaseModel):
  ad_id: str

class ReportIntegrated(BaseModel):
  dimensions: Dimensions

class ReportIntegratedPayload(BaseModel):
  list: list[ReportIntegrated]
  page_info: PageInfo

class ReportIntegratedResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: ReportIntegratedPayload

class Advertiser(BaseModel):
  advertiser_id: str
  advertiser_name: str

class AdvertiserPayload(BaseModel):
  list: list[Advertiser]

class AdvertiserResponse(BaseModel):
  code: int
  message: str
  request_id: str
  data: AdvertiserPayload
