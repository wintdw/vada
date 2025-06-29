### SOON DEPRECATED ### MOVE TO CRM
from uuid import uuid4

from models import Group
from tools import get_mysql_connection, get_mysql_cursor

async def insert_group(group: Group) -> Group:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            group.group_id = str(uuid4())
            await cursor.execute(
                "INSERT INTO `Group` (group_id, name, description, priority) VALUES (%s, %s, %s, %s)", (group.group_id, group.name, group.description, group.priority)
            )
            await connection.commit()
            return group

async def select_group(group_id: str) -> Group | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT group_id, name, description, priority FROM `Group` WHERE group_id = %s", (group_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return Group.model_validate(result)

async def select_groups() -> list[Group]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT group_id, name, description, priority FROM `Group`"
            )
            results = await cursor.fetchall()
            return [Group.model_validate(result) for result in results]

async def update_group(group_id: str, group: Group) -> Group:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "UPDATE `Group` SET name = %s, description = %s, priority = %s WHERE group_id = %s", (group.name, group.description, group.priority, group_id)
            )
            await connection.commit()
            group.group_id = group_id
            return group

async def remove_group(group_id: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "DELETE FROM `Group` WHERE group_id = %s", (group_id)
            )
            await connection.commit()
            return cursor.rowcount
