from models import UserGroup
from tools import get_mysql_connection, get_mysql_cursor

async def insert_user_group(user_group: UserGroup) -> UserGroup:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "INSERT INTO `UserGroup` (user_id, group_id) VALUES (%s, %s)", (user_group.user_id, user_group.group_id)
            )
            await connection.commit()
            return user_group

async def select_user_group(user_id: str, group_id: str) -> UserGroup | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT user_id, group_id FROM `UserGroup` WHERE user_id = %s, group_id = %s", (user_id, group_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return UserGroup.model_validate(result)

async def select_user_groups_by_user_id(user_id: str) -> list[UserGroup]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT user_id, group_id FROM `UserGroup` WHERE user_id = %s", (user_id)
            )
            results = await cursor.fetchall()
            return [UserGroup.model_validate(result) for result in results]

async def select_user_groups_by_group_id(group_id: str) -> list[UserGroup]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT user_id, group_id FROM `UserGroup` WHERE group_id = %s", (group_id)
            )
            results = await cursor.fetchall()
            return [UserGroup.model_validate(result) for result in results]

async def select_user_groups() -> list[UserGroup]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT user_id, group_id FROM `UserGroup`"
            )
            results = await cursor.fetchall()
            return [UserGroup.model_validate(result) for result in results]

async def remove_user_group(user_id: str, group_id: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "DELETE FROM `UserGroup` WHERE user_id = %s, group_id = %s", (user_id, group_id)
            )
            await connection.commit()
            return cursor.rowcount
