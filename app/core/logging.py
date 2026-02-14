"""Logging configuration for structured JSON logs."""

import logging
import sys
from pythonjsonlogger import json
from app.core.config import get_settings


settings = get_settings()

def setup_logging():
    """Setup structured logging for the application."""
    log_handler = logging.StreamHandler(sys.stdout)
    
    # Define log format and include standard fields
    formatter = json.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )

    
    log_handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(settings.log_level)
    
    # Silence some overly verbose third-party loggers
    logging.getLogger("uvicorn.access").handlers = [log_handler]
    logging.getLogger("uvicorn.error").handlers = [log_handler]
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Helper to get a logger instance."""
    return logging.getLogger(name)
