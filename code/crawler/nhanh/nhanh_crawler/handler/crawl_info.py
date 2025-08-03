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
    business_id: int,
    depot_ids: List,
    index_name: str,
    access_token: str,
    expired_datetime: str,
    crawl_interval: int,
) -> Dict:
    """
    Inserts a new record into the NhanhCrawlInfo table.
    We dont have vada_uid at this step
    """
    query = """
        INSERT INTO NhanhCrawlInfo (
            crawl_id, business_id, depot_ids, index_name,
            access_token, expired_datetime, crawl_interval, next_crawl_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() + INTERVAL %s MINUTE)
    """

    try:
        crawl_id = str(uuid.uuid4())

        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(
                    query,
                    (
                        crawl_id,
                        business_id,
                        json.dumps(depot_ids),
                        index_name,
                        access_token,
                        expired_datetime,
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
    crawl_id: str = "", business_id: int = 0, vada_uid: str = ""
) -> List[Dict]:
    """
    Selects info from NhanhCrawlInfo table, optionally filtered by crawl_id, business_id, and vada_uid.
    Only returns records where disabled = 0.
    If crawl_id is provided, business_id and vada_uid are ignored.
    """
    query = "SELECT * FROM NhanhCrawlInfo"
    params = []

    conditions = ["disabled = 0"]  # Always filter for enabled records
    if crawl_id:
        conditions.append("crawl_id = %s")
        params.append(crawl_id)
    else:
        if business_id:
            conditions.append("business_id = %s")
            params.append(business_id)
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
                "business_id": row["business_id"],
                "index_name": row["index_name"],
                "access_token": row["access_token"],
                "expired_datetime": (
                    row["expired_datetime"].isoformat()
                    if row["expired_datetime"]
                    else None
                ),
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
    for the specified crawl_id in the NhanhCrawlInfo table.
    """
    query = """
        UPDATE NhanhCrawlInfo
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
    crawl_id: str, access_token: str, expired_datetime: str
) -> Dict:
    """
    Updates the access_token and expired_datetime for a given crawl_id.
    """
    query = """
        UPDATE NhanhCrawlInfo
        SET access_token = %s,
            expired_datetime = %s
        WHERE crawl_id = %s
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query, (access_token, expired_datetime, crawl_id))
                await connection.commit()

        logging.info(
            f"Updated access_token and expired_datetime for crawl_id: {crawl_id}"
        )
        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(
            f"Error updating access_token for crawl_id {crawl_id}: {str(e)}",
            exc_info=True,
        )
        return {}


async def update_vada_uid(crawl_id: str, vada_uid: str) -> Dict:
    """
    Updates the vada_uid for a given crawl_id in the NhanhCrawlInfo table.
    """
    query = """
        UPDATE NhanhCrawlInfo
        SET vada_uid = %s
        WHERE crawl_id = %s
    """

    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute(query, (vada_uid, crawl_id))
                await connection.commit()

        logging.info(f"Updated vada_uid for crawl_id: {crawl_id}")
        return {"crawl_id": crawl_id}

    except Exception as e:
        logging.error(
            f"Error updating vada_uid for crawl_id {crawl_id}: {str(e)}",
            exc_info=True,
        )
        return {}


async def set_crawl_info(
    business_id: int,
    index_name: str = "",
    access_token: str = "",
    expired_datetime: str = "",
    crawl_interval: int = 1440,
    depot_ids: List = [],
) -> Dict:
    """
    Inserts or updates a record in NhanhCrawlInfo. Updates token and expiry if record exists.
    """
    try:
        result = await get_crawl_info(business_id=business_id)

        # If record exists, update token
        if result:
            crawl_id = result[0]["crawl_id"]

            if access_token:
                await update_crawl_token(crawl_id, access_token, expired_datetime)
                logging.info(
                    f"Updated access_token and expiry for crawl_id: {crawl_id}"
                )

            return {"crawl_id": crawl_id}

        else:
            insert_result = await insert_crawl_info(
                business_id=business_id,
                depot_ids=depot_ids,
                index_name=index_name,
                access_token=access_token,
                expired_datetime=expired_datetime,
                crawl_interval=crawl_interval,
            )
            logging.info(f"Inserted new crawl info for business_id: {business_id}")
            return insert_result

    except Exception as e:
        logging.error(f"Error setting crawl info: {str(e)}", exc_info=True)
        return {}
