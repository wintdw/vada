import aiomysql  # type: ignore
import logging
from contextlib import asynccontextmanager

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
