"""
Database initialization script
Creates necessary tables if they don't exist
"""
import asyncio
import logging
from handler.mysql import get_mysql_connection, get_mysql_cursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL để tạo bảng CrawlInfo
CREATE_CRAWLINFO_TABLE = """
CREATE TABLE IF NOT EXISTS CrawlInfo (
    crawl_id VARCHAR(36) PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    vada_uid VARCHAR(255) NOT NULL,
    index_name VARCHAR(255) DEFAULT '',
    crawl_type VARCHAR(50) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    crawl_interval INT DEFAULT 1440,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_account_vada (account_id, vada_uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

async def create_tables():
    """Create all necessary tables"""
    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                # Create CrawlInfo table
                logger.info("Creating CrawlInfo table if it doesn't exist...")
                await cursor.execute(CREATE_CRAWLINFO_TABLE)
                await connection.commit()
                logger.info("✅ CrawlInfo table created successfully")
                
                # Verify table exists
                await cursor.execute("SHOW TABLES LIKE 'CrawlInfo'")
                result = await cursor.fetchone()
                if result:
                    logger.info("✅ CrawlInfo table verified")
                else:
                    logger.error("❌ CrawlInfo table not found after creation")
                    
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        raise

async def check_database_connection():
    """Check if database connection is working"""
    try:
        async with get_mysql_connection() as connection:
            async with get_mysql_cursor(connection) as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                if result:
                    logger.info("✅ Database connection successful")
                    return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

async def main():
    """Main initialization function"""
    logger.info("🚀 Starting database initialization...")
    
    # Check connection first
    if not await check_database_connection():
        logger.error("❌ Cannot connect to database. Please check your configuration.")
        return False
    
    # Create tables
    await create_tables()
    logger.info("✅ Database initialization completed successfully")
    return True

if __name__ == "__main__":
    asyncio.run(main())
