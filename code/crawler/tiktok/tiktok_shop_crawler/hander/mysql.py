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
            connection.close()
            logging.debug("MySQL connection closed.")


@asynccontextmanager
async def get_mysql_cursor(connection):
    cursor = await connection.cursor(aiomysql.DictCursor)
    try:
        yield cursor
    finally:
        await cursor.close()


async def get_tiktok_shop_crawl_info() -> List[Dict]:
    """
    Selects index_name, access_token, and crawl_interval from CrawlInfo table
    where crawl_type is 'tiktok_shop'.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the selected information.
    """
    query = """
        SELECT *
        FROM CrawlInfo
        WHERE crawl_type = 'tiktok_shop'
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query)
                results = await cursor.fetchall()

        return [
            {
                "crawl_id": row["crawl_id"],
                "account_id": row["account_id"],
                "account_email": row["account_email"],
                "vada_uid": row["vada_uid"],
                "index_name": row["index_name"],
                "refresh_token": row["refresh_token"],
                "crawl_interval": row["crawl_interval"],
            }
            for row in results
        ]

    except Exception as e:
        logging.error(f"Error fetching Tiktok Shop crawl info: {str(e)}")
        return []


async def set_tiktok_shop_crawl_info(
    account_id: str,
    account_email: str,
    vada_uid: str,
    index_name: str,
    refresh_token: str,
    crawl_type: str = "tiktok_shop",
    crawl_interval: int = 1440,
) -> Dict:
    """
    Inserts a new record into the CrawlInfo table or updates the refresh token if the record exists.
    """
    crawl_id = str(uuid.uuid4())

    # Check if the record exists
    query_check = """
        SELECT crawl_id, account_id, account_email, vada_uid, index_name, refresh_token, crawl_interval
        FROM CrawlInfo
        WHERE account_id = %s AND vada_uid = %s
    """

    query_insert = """
        INSERT INTO CrawlInfo (
            crawl_id, account_id, account_email, vada_uid, index_name, crawl_type, access_token, 
            refresh_token, crawl_interval
        ) VALUES (%s, %s, %s, %s, %s, %s, "", %s, %s)
    """

    query_update = """
        UPDATE CrawlInfo
        SET refresh_token = %s
        WHERE account_id = %s AND vada_uid = %s
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query_check, (account_id, vada_uid))
                result = await cursor.fetchone()

                # If the record does not exist, insert it
                if not result:
                    await cursor.execute(
                        query_insert,
                        (
                            crawl_id,
                            account_id,
                            account_email,
                            vada_uid,
                            index_name,
                            crawl_type,
                            refresh_token,
                            crawl_interval,
                        ),
                    )
                    await connection.commit()
                    logging.info(f"Inserted crawl info for crawl_id: {crawl_id}")
                else:
                    # Update the refresh token if the record exists
                    await cursor.execute(
                        query_update,
                        (refresh_token, account_id, vada_uid),
                    )
                    await connection.commit()
                    logging.info(
                        f"Updated refresh token for account_id: {account_id} and vada_uid: {vada_uid}"
                    )
                    crawl_id = result["crawl_id"]
                    account_id = result["account_id"]
                    account_email = result["account_email"]
                    vada_uid = result["vada_uid"]
                    index_name = result["index_name"]
                    refresh_token = refresh_token  # Updated refresh token
                    crawl_interval = result["crawl_interval"]

        return {
            "crawl_id": crawl_id,
            "account_id": account_id,
            "account_email": account_email,
            "vada_uid": vada_uid,
            "index_name": index_name,
            "refresh_token": refresh_token,
            "crawl_interval": crawl_interval,
        }

    except Exception as e:
        logging.error(f"Error inserting or updating Google Ad crawl info: {str(e)}")
        return {}
