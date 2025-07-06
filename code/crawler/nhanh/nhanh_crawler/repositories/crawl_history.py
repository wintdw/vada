"""
Repository module for managing Nhanh crawl history in the database.

This module provides functions to interact with the NhanhCrawlHistory table,
including inserting new crawl history records and updating existing ones
with crawl results and status information.
"""

from uuid import uuid4

from models import NhanhCrawlHistory
from tools import get_mysql_connection, get_mysql_cursor


async def insert_crawl_history(crawl_history: NhanhCrawlHistory) -> NhanhCrawlHistory:
    """
    Insert a new crawl history record into the database.
    
    Creates a new entry in the NhanhCrawlHistory table to track the execution
    of a crawl operation. The function automatically generates a unique
    history_id using UUID4 and assigns it to the crawl_history object.
    
    Args:
        crawl_history (NhanhCrawlHistory): The crawl history object containing
                                          all necessary data for the operation.
                                          The history_id will be automatically
                                          generated and assigned.
    
    Returns:
        NhanhCrawlHistory: The crawl history object with the generated history_id
                          assigned. This is the same object that was passed in,
                          but with the history_id field populated.
        
    Raises:
        Exception: If database connection or query execution fails.
        
    Note:
        The function automatically commits the transaction after insertion.
    """
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            crawl_history.history_id = str(uuid4())
            await cursor.execute(
                """
                INSERT INTO `NhanhCrawlHistory`
                    (history_id, index_name, crawl_time, crawl_status,
                    crawl_error, crawl_duration, crawl_data_number) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    crawl_history.history_id,
                    crawl_history.index_name,
                    crawl_history.crawl_time,
                    crawl_history.crawl_status,
                    crawl_history.crawl_error,
                    crawl_history.crawl_duration,
                    crawl_history.crawl_data_number,
                ),
            )
            await connection.commit()
            return crawl_history


async def update_crawl_history(history_id: str, crawl_history: NhanhCrawlHistory) -> NhanhCrawlHistory:
    """
    Update an existing crawl history record in the database.
    
    Updates the NhanhCrawlHistory record identified by the provided history_id
    with new crawl status, error information, duration, and data count.
    This is typically used to update the final status of a crawl operation
    after it has completed or failed.
    
    Args:
        history_id (str): The unique identifier of the crawl history record
                         to be updated.
        crawl_history (NhanhCrawlHistory): The crawl history object containing
                                          the updated information to be stored.
                                          The history_id field will be set to
                                          match the provided history_id.
    
    Returns:
        NhanhCrawlHistory: The crawl history object with the history_id assigned.
                          This is the same object that was passed in, but with
                          the history_id field set to match the parameter.
        
    Raises:
        Exception: If database connection or query execution fails.
        
    Note:
        The function automatically commits the transaction after the update.
        If no record exists with the provided history_id, no rows will be
        affected but no error will be raised.
    """
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                UPDATE `NhanhCrawlHistory`
                SET crawl_status = %s,
                    crawl_error = %s,
                    crawl_duration = %s,
                    crawl_data_number = %s
                WHERE history_id = %s
                """,
                (
                    crawl_history.crawl_status,
                    crawl_history.crawl_error,
                    crawl_history.crawl_duration,
                    crawl_history.crawl_data_number,
                    history_id,
                ),
            )
            await connection.commit()
            crawl_history.history_id = history_id
            return crawl_history

