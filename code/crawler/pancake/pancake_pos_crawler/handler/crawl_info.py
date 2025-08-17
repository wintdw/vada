import uuid
import json
import logging
import aiomysql  # type: ignore

from contextlib import asynccontextmanager
from typing import Dict, List

from model.settings import settings


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
    vada_uid: str,
    index_name: str,
    api_token: str,
    crawl_interval: int,
) -> Dict:
    """
    Inserts a new record into the PCP table.
    """
    query = """
        INSERT INTO PCPCrawlInfo (
            crawl_id, vada_uid, index_name,
            api_token, crawl_interval, next_crawl_time
        )
        VALUES (%s, %s, %s, %s, %s, NOW() + INTERVAL %s MINUTE)
    """

    try:
        crawl_id = str(uuid.uuid4())

        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(
                    query,
                    (
                        crawl_id,
                        vada_uid,
                        index_name,
                        api_token,
                        crawl_interval,
                        crawl_interval,
                    ),
                )
                await connection.commit()

        logging.info(f"Inserted crawl info with crawl_id: {crawl_id}")
        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(f"Error inserting crawl info: {str(e)}", exc_info=True)
        return {}


async def get_crawl_info(
    crawl_id: str = "", index_name: str = "", vada_uid: str = ""
) -> List[Dict]:
    """
    Selects info from PCPCrawlInfo table, optionally filtered by crawl_id, index_name, and vada_uid.
    Only returns records where disabled = 0.
    If crawl_id is provided, index_name and vada_uid are ignored.
    """
    query = "SELECT * FROM PCPCrawlInfo"
    params = []

    conditions = ["disabled = 0"]  # Always filter for enabled records
    if crawl_id:
        conditions.append("crawl_id = %s")
        params.append(crawl_id)
    else:
        if index_name:
            conditions.append("business_id = %s")
            params.append(index_name)
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
                "vada_uid": row["vada_uid"],
                "index_name": row["index_name"],
                "api_token": row["api_token"],
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
            }
            for row in results
        ]

    except Exception as e:
        logging.error(f"Error fetching crawl info: {str(e)}", exc_info=True)
        return []


async def update_crawl_time(crawl_id: str, crawl_interval: int) -> Dict:
    """
    Updates last_crawl_time to NOW() and next_crawl_time to NOW() + INTERVAL crawl_interval MINUTE
    for the specified crawl_id in the PCPCrawlInfo table.
    """
    query = """
        UPDATE PCPCrawlInfo
        SET last_crawl_time = NOW(),
            next_crawl_time = NOW() + INTERVAL %s MINUTE
        WHERE crawl_id = %s
    """
    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query, (crawl_interval, crawl_id))
                await connection.commit()

        logging.info(f"Updated crawl time for crawl_id: {crawl_id}")
        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(
            f"Error updating crawl time for crawl_id {crawl_id}: {str(e)}",
            exc_info=True,
        )
        return {}


async def update_crawl_token(
    crawl_id: str, api_token: str
) -> Dict:
    """
    Updates the api_token for a given crawl_id.
    """
    query = """
        UPDATE PCPCrawlInfo
        SET api_token = %s
        WHERE crawl_id = %s
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query, (api_token, crawl_id))
                await connection.commit()

        logging.info(
            f"Updated api_token for crawl_id: {crawl_id}"
        )
        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(
            f"Error updating api_token for crawl_id {crawl_id}: {str(e)}",
            exc_info=True,
        )
        return {}

async def set_crawl_info(
    vada_uid: str = "",
    index_name: str = "",
    api_token: str = "",
    crawl_interval: int = 1440
) -> Dict:
    """
    Inserts or updates a record in PCPCrawlInfo. Updates token if record exists.
    """
    try:
        result = await get_crawl_info(index_name=index_name)

        # If record exists, update token
        if result:
            crawl_id = result[0]["crawl_id"]

            if api_token:
                await update_crawl_token(crawl_id, api_token)
                logging.info(
                    f"Updated api_token for crawl_id: {crawl_id}"
                )

            return {"crawl_id": crawl_id}

        else:
            insert_result = await insert_crawl_info(
                vada_uid=vada_uid,
                index_name=index_name,
                api_token=api_token,
                crawl_interval=crawl_interval
            )
            logging.info(f"Inserted new crawl info for index_name: {index_name}")
            return insert_result

    except Exception as e:
        logging.error(f"Error setting crawl info: {str(e)}", exc_info=True)
        return {}
