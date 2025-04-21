from time import time
import logging
from functools import wraps


def log_execution_time(func):
    """Decorator to log function execution time"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        result = await func(*args, **kwargs)
        execution_time = time() - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result

    return wrapper
