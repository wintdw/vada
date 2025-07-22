import aiomysql  # type: ignore

from contextlib import asynccontextmanager

from models.settings import settings
from .logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def get_mysql_connection():
    connection = None
    try:
        logger.debug("Initializing MySQL connection...")
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
            logger.debug("MySQL connection closed")


@asynccontextmanager
async def get_mysql_cursor(connection):
    cursor = await connection.cursor(aiomysql.DictCursor)
    try:
        yield cursor
    finally:
        await cursor.close()
