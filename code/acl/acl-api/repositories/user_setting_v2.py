from models import UserSetting_v2
from tools import get_mysql_connection, get_mysql_cursor

async def insert_user_setting_v2(user_setting: UserSetting_v2) -> UserSetting_v2:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            for permission in user_setting.setting.permissions:
                permission.clean()
            await cursor.execute(
                "INSERT INTO `UserSetting_v2` (workspace_id, user_id, setting) VALUES (%s, %s, %s)", (user_setting.workspace_id, user_setting.user_id, user_setting.setting.json())
            )
            await connection.commit()
            return user_setting

async def select_user_setting_by_workspace_id_and_user_id(workspace_id: str, user_id: str) -> UserSetting_v2 | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT workspace_id, user_id, setting FROM `UserSetting_v2` WHERE workspace_id = %s AND user_id = %s", (workspace_id, user_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return UserSetting_v2.model_validate(result)

async def update_user_setting_v2(workspace_id: str, user_id: str, user_setting: UserSetting_v2) -> UserSetting_v2:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            for permission in user_setting.setting.permissions:
                permission.clean()
            await cursor.execute(
                "UPDATE `UserSetting_v2` SET setting = %s WHERE workspace_id = %s AND user_id = %s", (user_setting.setting.json(), workspace_id, user_id)
            )
            await connection.commit()
            user_setting.workspace_id = workspace_id
            user_setting.user_id = user_id
            return user_setting