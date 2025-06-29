from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError
from tools import get_logger
from models import UserGroup, UserGroupResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.post("/v1/user_groups", response_model=UserGroupResponse, tags=["UserGroup"])
async def post_user_group(user_group: UserGroup):
    from repositories import insert_user_group

    try:
        await insert_user_group(user_group)
    except IntegrityError as e:
        logger.exception(e)
        return UserGroupResponse(
            status=409,
            message="Conflict",
            data=user_group
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(user_group)
    return UserGroupResponse(
        status=200,
        message="Success",
        data=user_group
    )

@router.get("/v1/user_groups/users/{user_id}", response_model=UserGroupResponse, tags=["UserGroup"])
async def get_user_group_by_user_id(user_id: str):
    from repositories import select_user_groups_by_user_id

    try:
        user_groups = await select_user_groups_by_user_id(user_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(user_groups)
    return UserGroupResponse(
        status=200,
        message="Success",
        data=user_groups
    )

@router.get("/v1/user_groups", response_model=UserGroupResponse, tags=["UserGroup"])
async def get_user_groups():
    from repositories import select_user_groups

    try:
        user_groups = await select_user_groups()
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(user_groups)
    return UserGroupResponse(
        status=200,
        message="Success",
        data=user_groups
    )

@router.delete("/v1/user_groups/{user_group_id}", response_model=UserGroupResponse, response_model_exclude_none=True, tags=["UserGroup"])
async def delete_user_group(user_group_id: str):
    from repositories import remove_user_group

    try:
        row_count = await remove_user_group(user_group_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if row_count > 0:
        return UserGroupResponse(
            status=200,
            message="Success"
        )
    else:
        return UserGroupResponse(
            status=404,
            message="Not Found"
        )
