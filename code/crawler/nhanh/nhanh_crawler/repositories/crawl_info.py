"""
Repository module for managing Nhanh crawl information in the database.

This module provides functions to interact with the NhanhCrawlInfo table,
including selecting records ready for crawling, removing records by index name,
and upserting crawl information.
"""

from uuid import uuid4
from typing import List

from models import NhanhCrawlInfo
from tools import get_mysql_connection, get_mysql_cursor


async def select_crawl_info_by_next_crawl_time() -> List[NhanhCrawlInfo]:
    """
    Select crawl information records that are ready for crawling.
    
    Retrieves all NhanhCrawlInfo records where the next_crawl_time
    is in the past (less than current time), indicating they are
    ready to be processed.
    
    Returns:
        List[NhanhCrawlInfo]: A list of crawl info records ready for processing.
        Each record contains business_id, access_token, depot_ids, expired_datetime, index_name,
        crawl_interval, last_crawl_time, and next_crawl_time.
        
    Raises:
        Exception: If database connection or query execution fails.
    """
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                SELECT index_name, business_id, access_token,
                    depot_ids, expired_datetime,
                    crawl_interval, last_crawl_time, next_crawl_time
                FROM `NhanhCrawlInfo`
                WHERE next_crawl_time < NOW()
                """
            )
            results = await cursor.fetchall()
            return [NhanhCrawlInfo.model_validate(result) for result in results]


async def update_crawl_info(index_name: str, crawl_info: NhanhCrawlInfo) -> NhanhCrawlInfo:
    """
    Update crawl information in the database.
    
    Updates the last_crawl_time and next_crawl_time fields for a given index_name.
    This is typically called after a successful crawl to update the scheduling
    information for the next crawl.
    
    Args:
        index_name (str): The unique index name identifying the crawl record to update.
        crawl_info (NhanhCrawlInfo): The crawl information object containing
                                    the updated last_crawl_time and next_crawl_time.
    
    Returns:
        NhanhCrawlInfo: The updated crawl info object.
        
    Raises:
        Exception: If database connection or query execution fails.
    """
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                UPDATE `NhanhCrawlInfo`
                SET
                    last_crawl_time = %s,
                    next_crawl_time = %s
                WHERE index_name = %s
                """,
                (
                    crawl_info.last_crawl_time,
                    crawl_info.next_crawl_time,
                    index_name
                )
            )
            await connection.commit()
            return crawl_info


async def remove_crawl_info_by_index_name(index_name: str) -> int:
    """
    Remove a crawl information record by its index name.
    
    Deletes the NhanhCrawlInfo record that matches the provided index_name.
    This is typically used when a crawl configuration is no longer needed
    or has been replaced.
    
    Args:
        index_name (str): The unique index name identifying the crawl record
                         to be removed.
    
    Returns:
        int: The number of rows affected (should be 0 or 1).
        
    Raises:
        Exception: If database connection or query execution fails.
    """
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            await cursor.execute(
                """
                DELETE FROM `NhanhCrawlInfo`
                WHERE index_name = %s
                """,
                (index_name,)
            )
            await connection.commit()
            return cursor.rowcount


async def upsert_crawl_info(crawl_info: NhanhCrawlInfo) -> NhanhCrawlInfo:
    """
    Insert or update crawl information in the database.
    
    This function performs an "upsert" operation (insert or update) on the
    NhanhCrawlInfo table. If a record with the same index_name exists,
    it updates the access_token and expired_datetime. If no record exists,
    it creates a new one with all the provided information.
    
    Args:
        crawl_info (NhanhCrawlInfo): The crawl information object containing
                                    all necessary data for the operation.
    
    Returns:
        NhanhCrawlInfo: The crawl info object that was inserted or updated.
                       This is typically the same object that was passed in.
        
    Raises:
        Exception: If database connection or query execution fails.
        
    Note:
        The function automatically commits the transaction for insert operations
        but not for update operations. This behavior should be reviewed for
        consistency.
    """
    async with get_mysql_connection() as connection:
        async with get_mysql_cursor(connection) as cursor:
            # Check if the record exists
            await cursor.execute(
                """
                SELECT index_name
                FROM `NhanhCrawlInfo`
                WHERE index_name = %s
                """,
                (crawl_info.index_name,)
            )
            existing_record = await cursor.fetchone()

            if existing_record:
                # Update the existing record
                await cursor.execute(
                    """
                    UPDATE `NhanhCrawlInfo`
                    SET
                        access_token = %s,
                        expired_datetime = %s
                    WHERE index_name = %s
                    """,
                    (
                        crawl_info.access_token,
                        crawl_info.expired_datetime,
                        crawl_info.index_name
                    )
                )
                await connection.commit()
            else:
                # Insert a new record
                await cursor.execute(
                    """
                    INSERT INTO `NhanhCrawlInfo`
                        (index_name, business_id, access_token, 
                        depot_ids, expired_datetime, crawl_interval)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, 
                    (
                        crawl_info.index_name,
                        crawl_info.business_id,
                        crawl_info.access_token,
                        crawl_info.depot_ids,
                        crawl_info.expired_datetime,
                        crawl_info.crawl_interval
                    )
                )
                await connection.commit()

            return crawl_info
