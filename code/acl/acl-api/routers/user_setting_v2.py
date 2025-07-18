from fastapi import APIRouter, HTTPException

from tools import get_logger
from models import UserSetting_v2, UserSettingResponse_v2, Setting

router = APIRouter()
logger = get_logger(__name__, 20)

### FE CALL ###
@router.get("/v1/user-settings/workspace/{workspace_id}/user/{user_id}", response_model=UserSettingResponse_v2, tags=["UserSetting_v2"])
async def get_user_setting_by_workspace_id_and_user_id(workspace_id: str, user_id: str):
    from repositories import select_user_setting_by_workspace_id_and_user_id

    try:
        user_setting = await select_user_setting_by_workspace_id_and_user_id(workspace_id, user_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if user_setting:
        logger.info(user_setting)
        return UserSettingResponse_v2(
            status=200,
            message="Success",
            data=user_setting
        )
    else:
        user_setting = UserSetting_v2(
            workspace_id=workspace_id,
            user_id=user_id,
            setting=Setting()
        )
        logger.info(user_setting)
        return UserSettingResponse_v2( 
            status=200,
            message="Success",
            data=user_setting
        )

### FE CALL ###
@router.put("/v1/user-settings/workspace/{workspace_id}/user/{user_id}", response_model=UserSettingResponse_v2, tags=["UserSetting_v2"])
async def put_user_setting_by_workspace_id_and_user_id(workspace_id: str, user_id: str, user_setting: UserSetting_v2):
    from repositories import select_user_setting_by_workspace_id_and_user_id, update_user_setting_v2, insert_user_setting_v2

    try:
        user_setting_selected = await select_user_setting_by_workspace_id_and_user_id(workspace_id, user_id)
        if user_setting_selected is None:
            user_setting = await insert_user_setting_v2(user_setting)
        else:
            user_setting = await update_user_setting_v2(workspace_id, user_id, user_setting)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(user_setting)
    return UserSettingResponse_v2(
        status=200,
        message="Success",
        data=user_setting
    )
