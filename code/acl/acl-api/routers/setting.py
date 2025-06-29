from fastapi import APIRouter, HTTPException

from tools import get_logger
from models import UserSetting, UserSettingResponse

router = APIRouter()
logger = get_logger(__name__, 20)

"""
### CRM CALL ###
@router.get("/v0/settings/users/{user_id}/indexes/{index_name}", response_model=UserSettingResponse, tags=["Setting"])
async def get_setting_by_index_name_v0(user_id: str, index_name: str):
    from repositories import select_user_setting
    from models import Filter, Permission, Setting

    try:
        user_setting = await select_user_setting(user_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if user_setting:
        for permission in user_setting.setting.permissions:
            if permission.index_name == index_name:
                user_setting.setting.permissions = permission
                return UserSettingResponse(
                    status=200,
                    message="Success",
                    data=user_setting
                )
        user_setting = UserSetting(
            user_id=user_id,
            setting=Setting(
                permissions=Permission(
                    index_name=index_name,
                    permit_filter=Filter()
                )
            )
        )
        logger.info(user_setting)
        return UserSettingResponse(
            status=200,
            message="Success",
            data=user_setting
        )
    else:
        user_setting = UserSetting(
            user_id=user_id,
            setting=Setting(
                permissions=Permission(
                    index_name=index_name,
                    permit_filter=Filter()
                )
            )
        )
        logger.info(user_setting)
        return UserSettingResponse(
            status=200,
            message="Success",
            data=user_setting
        )
"""
### CRM CALL ###
@router.get("/v1/settings/users/{user_id}/indexes/{index_name}", response_model=UserSettingResponse, tags=["Setting"])
async def get_setting_by_index_name(user_id: str, index_name: str):
    from repositories import select_user_setting, select_user_groups_by_user_id, select_group_setting
    from handlers import merge_permissions
    from models import Filter, Permission, Setting

    try:
        user_setting = await select_user_setting(user_id)
        if not user_setting or index_name not in [permissions.index_name for permissions in user_setting.setting.permissions]:
            user_setting = UserSetting(
                user_id=user_id,
                setting=Setting(
                    permissions=[Permission(
                        index_name=index_name,
                        permit_filter=Filter()
                    )]
                )
            )
        logger.debug(user_setting)
        user_groups = await select_user_groups_by_user_id(user_id)
        logger.debug(user_groups)
        for user_group in user_groups:
            group_setting = await select_group_setting(user_group.group_id)
            for permission in group_setting.setting.permissions:
                if permission.index_name == index_name:
                    user_setting.setting.permissions.append(permission)
        logger.debug(user_setting)
        user_setting = merge_permissions(user_setting)
        user_setting.setting.permissions = user_setting.setting.permissions[0]
        logger.info(user_setting)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return UserSettingResponse(
        status=200,
        message="Success",
        data=user_setting
    )

"""
### FE CALL ###
@router.get("/v0/settings/users/{user_id}", response_model=UserSettingResponse, tags=["Setting"])
async def get_setting_v0(user_id: str):
    from repositories import select_user_setting
    from models import Filter, Permission, Setting

    try:
        user_setting = await select_user_setting(user_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if user_setting:
        logger.info(user_setting)
        return UserSettingResponse(
            status=200,
            message="Success",
            data=user_setting
        )
    else:
        user_setting = UserSetting(
            user_id=user_id,
            setting=Setting()
        )
        logger.info(user_setting)
        return UserSettingResponse(
            status=200,
            message="Success",
            data=user_setting
        )
"""
@router.get("/v1/settings/users/{user_id}", response_model=UserSettingResponse, tags=["Setting"])
async def get_setting(user_id: str):
    from repositories import select_user_setting, select_user_groups_by_user_id, select_group_setting
    from handlers import merge_permissions
    from models import Setting

    try:
        user_setting = await select_user_setting(user_id)
        if not user_setting:
            user_setting = UserSetting(
                user_id=user_id,
                setting=Setting()
            )
        logger.debug(user_setting)
        user_groups = await select_user_groups_by_user_id(user_id)
        logger.debug(user_groups)
        for user_group in user_groups:
            group_setting = await select_group_setting(user_group.group_id)
            user_setting.setting.permissions.extend(group_setting.setting.permissions)
        logger.debug(user_setting)
        user_setting = merge_permissions(user_setting)
        logger.info(user_setting)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return UserSettingResponse(
        status=200,
        message="Success",
        data=user_setting
    )
