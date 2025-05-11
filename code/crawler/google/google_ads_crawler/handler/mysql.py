import os
import logging
import aiomysql  # type: ignore
from contextlib import asynccontextmanager

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
