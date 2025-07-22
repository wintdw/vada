import logging
import aiomysql  # type: ignore
import uuid
from contextlib import asynccontextmanager
from typing import List, Dict

from model.setting import settings


@asynccontextmanager
async def get_mysql_connection():
    connection = None
    try:
        logging.debug("Initializing MySQL connection...")
        connection = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWD,
            db=settings.MYSQL_DB,
        )
        yield connection
    finally:
        if connection:
            await connection.ensure_closed()
            logging.debug("MySQL connection closed")


@asynccontextmanager
async def get_mysql_cursor(connection):
    cursor = await connection.cursor(aiomysql.DictCursor)
    try:
        yield cursor
    finally:
        await cursor.close()


async def insert_crawl_info(
    account_id: str,
    vada_uid: str,
    account_name: str,
    index_name: str,
    refresh_token: str,
    access_token: str,
    access_token_expiry: int,
    refresh_token_expiry: int,
    crawl_interval: int = 1440,
) -> Dict:
    """
    Inserts a new record into the TTSCrawlInfo table.
    account_id and vada_uid are used to identify the record. The pair must be unique.
    """
    query = """
        INSERT INTO TTSCrawlInfo (
            crawl_id, account_id, account_name, vada_uid, index_name, access_token, 
            refresh_token, access_token_expiry, refresh_token_expiry, crawl_interval, next_crawl_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW() + INTERVAL %s MINUTE)
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                crawl_id = str(uuid.uuid4())
                await cursor.execute(
                    query,
                    (
                        crawl_id,
                        account_id,
                        account_name,
                        vada_uid,
                        index_name,
                        access_token,
                        refresh_token,
                        access_token_expiry,
                        refresh_token_expiry,
                        crawl_interval,
                        crawl_interval,
                    ),
                )
                await connection.commit()
                logging.info(
                    f"Inserted crawl info for account_name: {account_name} and vada_uid: {vada_uid}"
                )

        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(f"Error inserting crawl info: {str(e)}")
        return {}


async def get_crawl_info(
    crawl_id: str = "", account_id: str = "", vada_uid: str = ""
) -> List[Dict]:
    """
    Selects info from TTSCrawlInfo table, optionally filtered by crawl_id, account_id, and vada_uid.
    Only returns records where disabled = 0.
    If crawl_id is provided, account_id and vada_uid are ignored.
    """
    query = "SELECT * FROM TTSCrawlInfo"
    params = []

    conditions = ["disabled = 0"]  # Always filter for enabled records
    if crawl_id:
        conditions.append("crawl_id = %s")
        params.append(crawl_id)
    else:
        if account_id:
            conditions.append("account_id = %s")
            params.append(account_id)
        if vada_uid:
            conditions.append("vada_uid = %s")
            params.append(vada_uid)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query, tuple(params))
                results = await cursor.fetchall()

        return [
            {
                "crawl_id": row["crawl_id"],
                "account_id": row["account_id"],
                "account_name": row["account_name"],
                "vada_uid": row["vada_uid"],
                "index_name": row["index_name"],
                "access_token": row["access_token"],
                "refresh_token": row["refresh_token"],
                "access_token_expiry": row["access_token_expiry"],
                "refresh_token_expiry": row["refresh_token_expiry"],
                "crawl_interval": row["crawl_interval"],
                "last_crawl_time": (
                    row["last_crawl_time"].isoformat()
                    if row["last_crawl_time"]
                    else None
                ),
                "next_crawl_time": (
                    row["next_crawl_time"].isoformat()
                    if row["next_crawl_time"]
                    else None
                ),
                "created_at": (
                    row["created_at"].isoformat() if row["created_at"] else None
                ),
                "updated_at": (
                    row["updated_at"].isoformat() if row["updated_at"] else None
                ),
            }
            for row in results
        ]

    except Exception as e:
        logging.error(f"Error fetching crawl info: {str(e)}")
        return []


async def update_crawl_time(crawl_id: str, crawl_interval: int) -> Dict:
    """
    Updates last_crawl_time to NOW() and next_crawl_time to NOW() + INTERVAL crawl_interval MINUTE.
    """
    query = """
        UPDATE TTSCrawlInfo
        SET last_crawl_time = NOW(),
            next_crawl_time = NOW() + INTERVAL %s MINUTE
        WHERE crawl_id = %s
    """
    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query, (crawl_interval, crawl_id))
                await connection.commit()
        return {"crawl_id": crawl_id}
    except Exception as e:
        logging.error(f"Error updating crawl time: {str(e)}")
        return {}


async def update_crawl_token(
    crawl_id: str,
    access_token: str,
    refresh_token: str,
    access_token_expiry: int,
    refresh_token_expiry: int,
) -> Dict:
    """Updates the access_token, refresh_token, and their expiry times for a given crawl_id."""
    query = """
        UPDATE TTSCrawlInfo
        SET access_token = %s, refresh_token = %s,
            access_token_expiry = %s, refresh_token_expiry = %s
        WHERE crawl_id = %s
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(
                    query,
                    (
                        access_token,
                        refresh_token,
                        access_token_expiry,
                        refresh_token_expiry,
                        crawl_id,
                    ),
                )
                await connection.commit()
                logging.info(f"Updated tokens and expiry for crawl_id: {crawl_id}")

        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(f"Error updating crawl tokens: {str(e)}")
        return {}


async def set_crawl_info(
    account_id: str,
    vada_uid: str,
    account_name: str = "",
    index_name: str = "",
    access_token: str = "",
    refresh_token: str = "",
    access_token_expiry: int = 0,
    refresh_token_expiry: int = 0,
    crawl_interval: int = 1440,
) -> Dict:
    """
    Inserts a new record into the CrawlInfo table or updates the tokens and expiry if the record exists.
    account_id and vada_uid are used to identify the record. The pair must be unique.
    """
    try:
        result = await get_crawl_info(account_id=account_id, vada_uid=vada_uid)

        if result:
            # If the record exists, update the tokens and expiry
            crawl_id = result[0]["crawl_id"]
            account_name = result[0]["account_name"]
            index_name = result[0]["index_name"]

            if (
                access_token
                and refresh_token
                and access_token_expiry
                and refresh_token_expiry
            ):
                await update_crawl_token(
                    crawl_id,
                    access_token,
                    refresh_token,
                    access_token_expiry,
                    refresh_token_expiry,
                )
                logging.info(
                    f"Updated tokens for account_name: {account_name} and vada_uid: {vada_uid}"
                )

            return {"crawl_id": crawl_id}
        else:
            # insert a new record
            insert_result = await insert_crawl_info(
                account_id,
                vada_uid,
                account_name,
                index_name,
                refresh_token,
                access_token,
                access_token_expiry,
                refresh_token_expiry,
                crawl_interval,
            )
            logging.info(
                f"Inserted crawl info for account_name: {account_name} and vada_uid: {vada_uid}"
            )
            return insert_result
    except Exception as e:
        logging.error(f"Error setting crawl info: {str(e)}")
        return {}
