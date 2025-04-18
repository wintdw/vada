from uuid import uuid4

from models import CrawlInfo
from tools import get_mysql_connection, get_mysql_cursor

async def insert_crawl_info(crawl_info: CrawlInfo) -> CrawlInfo:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            crawl_info.crawl_id = str(uuid4())
            await cursor.execute(
                "INSERT INTO `CrawlInfo` (crawl_id, index_name, access_token, refresh_token, crawl_interval, next_crawl_time) VALUES (%s, %s, %s, %s, %s, %s)", (crawl_info.crawl_id, crawl_info.index_name, crawl_info.access_token, crawl_info.refresh_token, crawl_info.crawl_interval, crawl_info.next_crawl_time)
            )
            await connection.commit()
            return crawl_info

async def select_crawl_info(crawl_id: str) -> CrawlInfo | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT crawl_id, index_name, access_token, refresh_token, access_token_updated_at, crawl_interval, last_crawl_time, next_crawl_time FROM `CrawlInfo` WHERE crawl_id = %s", (crawl_id)
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return CrawlInfo.model_validate(result)

async def select_crawl_infos() -> list[CrawlInfo]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "SELECT crawl_id, index_name, access_token, refresh_token, access_token_updated_at, crawl_interval, last_crawl_time, next_crawl_time FROM `CrawlInfo`"
            )
            results = await cursor.fetchall()
            return [CrawlInfo.model_validate(result) for result in results]

async def update_crawl_info(crawl_id: str, crawl_info: CrawlInfo) -> CrawlInfo:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "UPDATE `CrawlInfo` SET access_token_updated_at = %s, crawl_interval = %s, last_crawl_time = %s, next_crawl_time = %s WHERE crawl_id = %s", (crawl_info.access_token_updated_at, crawl_info.crawl_interval, crawl_info.last_crawl_time, crawl_info.next_crawl_time, crawl_id)
            )
            await connection.commit()
            crawl_info.crawl_id = crawl_id
            return crawl_info

async def remove_crawl_info(crawl_id: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                "DELETE FROM `CrawlInfo` WHERE crawl_id = %s", (crawl_id)
            )
            await connection.commit()
            return cursor.rowcount