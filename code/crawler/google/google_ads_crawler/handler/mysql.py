import os
import logging
import aiomysql  # type: ignore
import uuid
from datetime import datetime, timedelta
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


async def set_google_ad_crawl_info(
    index_name: str,
    refresh_token: str,
    crawl_type: str = "google_ad",
    crawl_interval: int = 1440,
):
    """
    Inserts a new record into the CrawlInfo table.

    Args:
        index_name (str): The index name.
        crawl_type (str): The type of crawl.
        refresh_token (str): The refresh token.
        crawl_interval (int): The crawl interval in minutes.
    """
    crawl_id = str(uuid.uuid4())

    # Calculate crawl_from_date and crawl_to_date
    crawl_from_date = (datetime.now() - timedelta(days=365)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    crawl_to_date = (datetime.now() + timedelta(days=3650)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    query = """
        INSERT INTO CrawlInfo (
            crawl_id, index_name, crawl_type, refresh_token,
            crawl_interval, crawl_from_date, crawl_to_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(
                    query,
                    (
                        crawl_id,
                        index_name,
                        crawl_type,
                        refresh_token,
                        crawl_interval,
                        crawl_from_date,
                        crawl_to_date,
                    ),
                )
                await connection.commit()
                logging.info(f"Inserted crawl info for crawl_id: {crawl_id}")

    except Exception as e:
        logging.error(f"Error inserting Google Ad crawl info: {str(e)}")
