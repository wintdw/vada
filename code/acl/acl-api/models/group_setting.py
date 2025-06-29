from pydantic import BaseModel, validator
import json

from .setting import Setting

class GroupSetting(BaseModel):
    group_id: str
    setting: Setting

    @validator('setting', pre=True)
    def parse_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value

class GroupSettingResponse(BaseModel):
    status: int
    message: str
    data: list[GroupSetting] | GroupSetting = []
