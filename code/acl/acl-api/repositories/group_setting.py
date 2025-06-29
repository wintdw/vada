from models import GroupSetting
from tools import get_mysql_connection, get_mysql_cursor

async def insert_group_setting(group_setting: GroupSetting) -> GroupSetting:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            for permission in group_setting.setting.permissions:
                permission.clean()
            await cursor.execute(
                "INSERT INTO `GroupSetting` (group_id, setting) VALUES (%s, %s)", (group_setting.group_id, group_setting.setting.json())
            )
            await connection.commit()
            return group_setting

async def select_group_setting(group_id: str) -> GroupSetting | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT group_id, setting FROM `GroupSetting` WHERE group_id = %s", (group_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return GroupSetting.model_validate(result)

async def select_group_settings() -> list[GroupSetting]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT group_id, setting FROM `GroupSetting`"
            )
            results = await cursor.fetchall()
            return [GroupSetting.model_validate(result) for result in results]

async def update_group_setting(group_id: str, group_setting: GroupSetting) -> GroupSetting:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            for permission in group_setting.setting.permissions:
                permission.clean()
            await cursor.execute(
                "UPDATE `GroupSetting` SET setting = %s WHERE group_id = %s", (group_setting.setting.json(), group_id)
            )
            await connection.commit()
            group_setting.group_id = group_id
            return group_setting

async def remove_group_setting(group_id: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "DELETE FROM `GroupSetting` WHERE group_id = %s", (group_id)
            )
            await connection.commit()
            return cursor.rowcount
