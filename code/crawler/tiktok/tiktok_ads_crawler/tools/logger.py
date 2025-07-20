import logging
import sys
import json
from pythonjsonlogger import jsonlogger  # type: ignore
from datetime import datetime, timezone, timedelta
import contextvars

# Define GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

# Create a context variable to store the request ID
request_id = contextvars.ContextVar("request_id", default="")


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter to match the required log payload structure."""

    def format(self, record):
        # Convert timestamp to GMT+7
        record.timestamp = datetime.now(GMT_PLUS_7).isoformat()

        # Create a structured log payload
        log_payload = {
            "timestamp": record.timestamp,
            "level": record.levelname,
            "logger_name": record.name,
            "module": record.pathname,
            "line": record.lineno,
            "request_id": request_id.get(),
            "message": record.getMessage(),
        }

        return json.dumps(log_payload, ensure_ascii=False)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        log_handler = logging.StreamHandler(sys.stdout)
        log_formatter = CustomJsonFormatter()
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        logger.propagate = False  # <--- Add this line

    return logger
