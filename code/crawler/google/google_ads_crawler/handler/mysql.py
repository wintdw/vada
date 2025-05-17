import os
import logging
import aiomysql  # type: ignore
import uuid
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import List, Dict

from model.setting import settings


mysql_passwd_file = settings.MYSQL_PASSWD_FILE
if mysql_passwd_file and os.path.isfile(mysql_passwd_file):
    with open(mysql_passwd_file, "r") as file:
        mysql_passwd = file.read().strip()


@asynccontextmanager
async def get_mysql_connection():
    connection = None
    try:
        logging.debug("Initializing MySQL connection...")
        connection = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=mysql_passwd,
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


async def get_google_ad_crawl_info() -> List[Dict]:
    """
    Selects index_name, access_token, and crawl_interval from CrawlInfo table
    where crawl_type is 'google_ad'.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the selected information.
    """
    query = """
        SELECT *
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
        logging.error(f"Error fetching Google Ad crawl info: {str(e)}")
        return []


async def set_google_ad_crawl_info(
    account_id: str,
    account_email: str,
    vada_uid: str,
    index_name: str,
    refresh_token: str,
    crawl_type: str = "google_ad",
    crawl_interval: int = 1440,
) -> Dict:
    """
    Inserts a new record into the CrawlInfo table.
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
            crawl_id, account_id, account_email, vada_uid, index_name, crawl_type, access_token, refresh_token,
            crawl_interval, crawl_from_date, crawl_to_date
        ) VALUES (%s, %s, %s, %s, %s, %s, "", %s, %s, %s, %s)
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(
                    query,
                    (
                        crawl_id,
                        account_id,
                        account_email,
                        vada_uid,
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
        logging.error(f"Error inserting Google Ad crawl info: {str(e)}")
        return {}
