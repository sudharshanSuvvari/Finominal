import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

from app.core.config import settings

# Global logger instance
_logger = None
_is_configured = False

def configure_logging():
    """
    Configure simple logging system with single logger and single log file
    """
    global _logger, _is_configured
    
    if _is_configured:
        return _logger
    
    # Ensure logs directory exists
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Single log file
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create logger
    _logger = logging.getLogger("zorvyn_api")
    _logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Remove any existing handlers to avoid duplicates
    for handler in _logger.handlers[:]:
        _logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=os.getenv(
            "LOG_FORMAT", 
            "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
        ),
        datefmt=settings.LOG_DATE_FORMAT
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    # Prevent propagation to root logger to avoid duplicates
    _logger.propagate = False
    
    _is_configured = True
    _logger.info("Logging system configured successfully")
    
    return _logger

def get_logger():
    """
    Get the common logger instance
    """
    if not _is_configured:
        return configure_logging()
    return _logger