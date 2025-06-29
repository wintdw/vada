from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError

from tools import get_logger
from models import Group, GroupResponse

router = APIRouter()
logger = get_logger(__name__, 20)

### FE CALL ###
@router.post("/v1/groups", response_model=GroupResponse, tags=["Group"])
async def post_group(group: Group):
    from repositories import insert_group

    try:
        await insert_group(group)
    except IntegrityError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=409,
            detail="Conflict"
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(group)
    return GroupResponse(
        status=201,
        message="Created",
        data=group
    )

### FE CALL ###
@router.get("/v1/groups/{group_id}", response_model=GroupResponse, tags=["Group"])
async def get_group(group_id: str):
    from repositories import select_group

    try:
        group = await select_group(group_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    else:
        logger.info(group)
        return GroupResponse(
            status=200,
            message="Success",
            data=group
        )

### FE CALL ###
@router.get("/v1/groups", response_model=GroupResponse, tags=["Group"])
async def get_groups():
    from repositories import select_groups

    try:
        groups = await select_groups()
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(groups)
    return GroupResponse(
        status=200,
        message="Success",
        data=groups
    )

### FE CALL ###
@router.put("/v1/groups/{group_id}", response_model=GroupResponse, tags=["Group"])
async def put_group(group_id: str, group: Group):
    from repositories import select_group, update_group

    try:
        group_selected = await select_group(group_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if group_selected is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    else:
        try:
            group = await update_group(group_id, group)
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error"
            )
        logger.info(group)
        return GroupResponse(
            status=200,
            message="Success",
            data=group
        )

### FE CALL ###
@router.delete("/v1/groups/{group_id}", response_model=GroupResponse, response_model_exclude_none=True, tags=["Group"])
async def delete_group(group_id: str):
    from repositories import remove_group

    try:
        row_count = await remove_group(group_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    if row_count > 0:
        return GroupResponse(
            status=200,
            message="Success"
        )
    else:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
