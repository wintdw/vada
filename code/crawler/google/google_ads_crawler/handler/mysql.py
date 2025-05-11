import os
import logging
import aiomysql  # type: ignore
from contextlib import asynccontextmanager
from typing import List, Dict

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_DB = os.getenv("MYSQL_DB")
mysql_passwd_file = os.getenv("MYSQL_PASSWD_FILE")
if mysql_passwd_file and os.path.isfile(mysql_passwd_file):
    with open(mysql_passwd_file, "r") as file:
        MYSQL_PASSWD = file.read().strip()


@asynccontextmanager
async def get_mysql_connection():
    connection = None
    try:
        logging.debug("Initializing MySQL connection...")
        connection = await aiomysql.connect(
            host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWD, db=MYSQL_DB
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


async def get_google_ad_crawl_info() -> List[Dict]:
    """
    Selects index_name, access_token, and crawl_interval from CrawlInfo table
    where crawl_type is 'google_ad'.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the selected information.
    """
    query = """
        SELECT crawl_id, index_name, refresh_token, crawl_interval
        FROM CrawlInfo
        WHERE crawl_type = 'google_ad'
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query)
                results = await cursor.fetchall()

        return [
            {
                "crawl_id": row["crawl_id"],
                "index_name": row["index_name"],
                "refresh_token": row["refresh_token"],
                "crawl_interval": row["crawl_interval"],
            }
            for row in results
        ]

    except Exception as e:
        logging.error(f"Error fetching Google Ad crawl info: {str(e)}")
        return []
