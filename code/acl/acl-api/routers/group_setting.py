from fastapi import APIRouter, HTTPException

from tools import get_logger
from models import GroupSetting, GroupSettingResponse, Setting

router = APIRouter()
logger = get_logger(__name__, 20)

### FE CALL ###
@router.get("/v1/group-settings/{group_id}", response_model=GroupSettingResponse, tags=["GroupSetting"])
async def get_group_setting(group_id: str):
    from repositories import select_group_setting

    try:
        group_setting = await select_group_setting(group_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if group_setting:
        logger.info(group_setting)
        return GroupSettingResponse(
            status=200,
            message="Success",
            data=group_setting
        )
    else:
        group_setting = GroupSetting(
            group_id=group_id,
            setting=Setting()
        )
        logger.info(group_setting)
        return GroupSettingResponse( 
            status=200,
            message="Success",
            data=group_setting
        )

@router.get("/v1/group-settings", response_model=GroupSettingResponse, tags=["GroupSetting"])
async def get_group_settings():
    from repositories import select_group_settings

    try:
        group_settings = await select_group_settings()
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(group_settings)
    return GroupSettingResponse(
        status=200,
        message="Success",
        data=group_settings
    )

### FE CALL ###
@router.put("/v1/group-settings/{group_id}", response_model=GroupSettingResponse, tags=["GroupSetting"])
async def put_group_setting(group_id: str, group_setting: GroupSetting):
    from repositories import select_group_setting, update_group_setting, insert_group_setting

    try:
        group_setting_selected = await select_group_setting(group_id)
        if group_setting_selected is None:
            group_setting = await insert_group_setting(group_setting)
        else:
            group_setting = await update_group_setting(group_id, group_setting)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(group_setting)
    return GroupSettingResponse(
        status=200,
        message="Success",
        data=group_setting
    )
