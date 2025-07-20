from uuid import uuid4

from models import CrawlInfo
from tools import get_mysql_connection, get_mysql_cursor


async def insert_crawl_info(crawl_info: CrawlInfo) -> CrawlInfo:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            crawl_info.crawl_id = str(uuid4())
            await cursor.execute(
                """
                INSERT INTO `CrawlInfo`
                    (crawl_id, account_id, account_name, vada_uid,
                    index_name, crawl_type, access_token, refresh_token,
                    crawl_interval)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    crawl_info.crawl_id,
                    crawl_info.account_id,
                    crawl_info.account_name,
                    crawl_info.vada_uid,
                    crawl_info.index_name,
                    crawl_info.crawl_type,
                    crawl_info.access_token,
                    crawl_info.refresh_token,
                    crawl_info.crawl_interval,
                ),
            )
            await connection.commit()
            return crawl_info


async def select_crawl_info_by_crawl_id(crawl_id: str) -> CrawlInfo | None:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                SELECT crawl_id, account_id, account_name, vada_uid,
                    index_name, crawl_type, access_token, refresh_token,
                    access_token_updated_at, refresh_token_updated_at,
                    crawl_interval, last_crawl_time, next_crawl_time
                FROM `CrawlInfo`
                WHERE crawl_id = %s
                """,
                (crawl_id),
            )
            result = await cursor.fetchone()
            if result is None:
                return None
            else:
                return CrawlInfo.model_validate(result)


async def select_crawl_info_by_next_crawl_time() -> list[CrawlInfo]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                SELECT crawl_id, account_id, account_name, vada_uid,
                    index_name, crawl_type, access_token, refresh_token,
                    access_token_updated_at, refresh_token_updated_at,
                    crawl_interval, last_crawl_time, next_crawl_time
                FROM `CrawlInfo`
                WHERE next_crawl_time < NOW() AND crawl_type = 'tiktok_business_ads'
                """
            )
            results = await cursor.fetchall()
            return [CrawlInfo.model_validate(result) for result in results]


async def select_crawl_info() -> list[CrawlInfo]:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                SELECT crawl_id, account_id, account_name, vada_uid,
                    index_name, crawl_type, access_token, refresh_token,
                    access_token_updated_at, refresh_token_updated_at,
                    crawl_interval, last_crawl_time, next_crawl_time
                FROM `CrawlInfo`
                """
            )
            results = await cursor.fetchall()
            return [CrawlInfo.model_validate(result) for result in results]


async def update_crawl_info(crawl_id: str, crawl_info: CrawlInfo) -> CrawlInfo:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                UPDATE `CrawlInfo`
                SET account_id = %s,
                    account_name = %s,
                    vada_uid = %s,
                    index_name = %s,
                    crawl_type = %s,
                    access_token = %s,
                    refresh_token = %s,
                    access_token_updated_at = %s,
                    refresh_token_updated_at = %s,
                    crawl_interval = %s,
                    last_crawl_time = %s,
                    next_crawl_time = %s
                WHERE crawl_id = %s
                """,
                (
                    crawl_info.account_id,
                    crawl_info.account_name,
                    crawl_info.vada_uid,
                    crawl_info.index_name,
                    crawl_info.crawl_type,
                    crawl_info.access_token,
                    crawl_info.refresh_token,
                    crawl_info.access_token_updated_at,
                    crawl_info.refresh_token_updated_at,
                    crawl_info.crawl_interval,
                    crawl_info.last_crawl_time,
                    crawl_info.next_crawl_time,
                    crawl_id,
                ),
            )
            await connection.commit()
            crawl_info.crawl_id = crawl_id
            return crawl_info


async def remove_crawl_info_by_crawl_id(crawl_id: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                DELETE FROM `CrawlInfo`
                WHERE crawl_id = %s
                """,
                (crawl_id),
            )
            await connection.commit()
            return cursor.rowcount


async def remove_crawl_info_by_index_name(index_name: str) -> int:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                DELETE FROM `CrawlInfo`
                WHERE index_name = %s
                """,
                (index_name),
            )
            await connection.commit()
            return cursor.rowcount


async def upsert_crawl_info(crawl_info: CrawlInfo) -> CrawlInfo:
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            # Check if the record exists
            await cursor.execute(
                """
                SELECT crawl_id
                FROM `CrawlInfo`
                WHERE account_id = %s AND vada_uid = %s
                """,
                (crawl_info.account_id, crawl_info.vada_uid),
            )
            existing_record = await cursor.fetchone()

            if existing_record:
                # Update the existing record
                await cursor.execute(
                    """
                    UPDATE `CrawlInfo`
                    SET
                        access_token = %s,
                        refresh_token = %s,
                        access_token_updated_at = NOW(),
                        refresh_token_updated_at = NOW()
                    WHERE crawl_id = %s
                    """,
                    (
                        crawl_info.access_token,
                        crawl_info.refresh_token,
                        crawl_info.crawl_id,
                    ),
                )
            else:
                # Insert a new record
                crawl_info.crawl_id = str(uuid4())
                await cursor.execute(
                    """
                    INSERT INTO `CrawlInfo`
                        (crawl_id, account_id, account_name, vada_uid,
                        index_name, crawl_type, access_token, refresh_token,
                        crawl_interval)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        crawl_info.crawl_id,
                        crawl_info.account_id,
                        crawl_info.account_name,
                        crawl_info.vada_uid,
                        crawl_info.index_name,
                        crawl_info.crawl_type,
                        crawl_info.access_token,
                        crawl_info.refresh_token,
                        crawl_info.crawl_interval,
                    ),
                )
                await connection.commit()

            return crawl_info
