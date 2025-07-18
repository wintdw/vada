from models import UserSetting
from tools import get_mysql_connection, get_mysql_cursor

async def insert_user_setting(user_setting: UserSetting) -> UserSetting:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            for permission in user_setting.setting.permissions:
                permission.clean()
            await cursor.execute(
                "INSERT INTO `UserSetting` (user_id, setting) VALUES (%s, %s)", (user_setting.user_id, user_setting.setting.json())
            )
            await connection.commit()
            return user_setting

async def select_user_setting_by_user_id(user_id: str) -> UserSetting | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT user_id, setting FROM `UserSetting` WHERE user_id = %s", (user_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return UserSetting.model_validate(result)

async def update_user_setting(user_id: str, user_setting: UserSetting) -> UserSetting:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            for permission in user_setting.setting.permissions:
                permission.clean()
            await cursor.execute(
                "UPDATE `UserSetting` SET setting = %s WHERE user_id = %s", (user_setting.setting.json(), user_id)
            )
            await connection.commit()
            user_setting.user_id = user_id
            return user_setting
