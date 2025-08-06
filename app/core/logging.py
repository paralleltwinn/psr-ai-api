# =============================================================================
# POORNASREE AI - LOGGING CONFIGURATION
# =============================================================================

"""
Centralized logging configuration for the application.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any
import sys

from ..config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to levelname
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


def setup_logging() -> Dict[str, Any]:
    """Setup application logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_specific_loggers()
    
    return {
        "console_handler": console_handler,
        "file_handler": file_handler,
        "log_level": settings.log_level,
        "log_file": settings.log_file
    }


def configure_specific_loggers():
    """Configure specific loggers for different components."""
    
    # Database logger
    db_logger = logging.getLogger("sqlalchemy.engine")
    db_logger.setLevel(logging.WARNING if not settings.debug else logging.INFO)
    
    # Alembic logger
    alembic_logger = logging.getLogger("alembic")
    alembic_logger.setLevel(logging.INFO)
    
    # FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # Application specific loggers
    auth_logger = logging.getLogger("app.auth")
    auth_logger.setLevel(logging.INFO)
    
    email_logger = logging.getLogger("app.email")
    email_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()
