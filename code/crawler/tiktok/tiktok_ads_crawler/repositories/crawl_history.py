from uuid import uuid4

from models import CrawlHistory
from tools import get_mysql_connection, get_mysql_cursor

async def insert_crawl_history(crawl_history: CrawlHistory) -> CrawlHistory:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            crawl_history.history_id = str(uuid4())
            await cursor.execute(
                "INSERT INTO `CrawlHistory` (history_id, crawl_id, crawl_status, crawl_error, crawl_duration, crawl_data_number, crawl_from_date, crawl_to_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (crawl_history.history_id, crawl_history.crawl_id, crawl_history.crawl_status, crawl_history.crawl_error, crawl_history.crawl_duration, crawl_history.crawl_data_number, crawl_history.crawl_from_date, crawl_history.crawl_to_date)
            )
            await connection.commit()
            return crawl_history

async def select_crawl_history_by_crawl_id(crawl_id: str) -> CrawlHistory | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT history_id, crawl_id, crawl_time, crawl_status, crawl_error, crawl_duration, crawl_data_number, crawl_from_date, crawl_to_date FROM `CrawlHistory` WHERE crawl_id = %s", (crawl_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return CrawlHistory.model_validate(result)

async def select_crawl_history() -> list[CrawlHistory]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT history_id, crawl_id, crawl_time, crawl_status, crawl_error, crawl_duration, crawl_data_number, crawl_from_date, crawl_to_date FROM `CrawlHistory`"
            )
            results = await cursor.fetchall()
            return [CrawlHistory.model_validate(result) for result in results]

async def update_crawl_history(history_id: str, crawl_history: CrawlHistory) -> CrawlHistory:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "UPDATE `CrawlHistory` SET crawl_status = %s, crawl_error = %s, crawl_duration = %s, crawl_data_number = %s WHERE history_id = %s", (crawl_history.crawl_status, crawl_history.crawl_error, crawl_history.crawl_duration, crawl_history.crawl_data_number, history_id)
            )
            await connection.commit()
            crawl_history.history_id = history_id
            return crawl_history

async def remove_crawl_history(history_id: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "DELETE FROM `CrawlHistory` WHERE crawl_id = %s", (history_id)
            )
            await connection.commit()
            return cursor.rowcount
