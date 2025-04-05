import logging
import sys
import json
from pythonjsonlogger import jsonlogger
from datetime import datetime, timezone, timedelta

# Define GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter to match the required log payload structure."""

    def format(self, record):
        # Convert timestamp to GMT+7
        record.timestamp = datetime.now(GMT_PLUS_7).isoformat()

        # Create a structured log payload
        log_payload = {
            "timestamp": record.timestamp,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "module": record.pathname,
            "line": record.lineno,
        }

        return json.dumps(log_payload, ensure_ascii=False)

def get_logger(name: str, level: int = logging.INFO):
    """Returns a structured JSON logger with GMT+7 timestamps."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        log_handler = logging.StreamHandler(sys.stdout)
        log_formatter = CustomJsonFormatter()
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)

    return logger
