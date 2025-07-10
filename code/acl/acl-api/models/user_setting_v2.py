from pydantic import BaseModel, validator
import json

from .setting import Setting

class UserSetting_v2(BaseModel):
    workspace_id: str
    user_id: str
    setting: Setting

    @validator('setting', pre=True)
    def parse_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value

class UserSettingResponse_v2(BaseModel):
    status: int
    message: str
    data: list[UserSetting_v2] | UserSetting_v2 = []