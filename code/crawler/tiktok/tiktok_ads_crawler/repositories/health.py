from tools import get_mysql_connection, get_mysql_cursor

async def health_check() -> bool:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT 1"
            )
            return True