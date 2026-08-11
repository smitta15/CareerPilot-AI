"""
Centralized logging configuration for CareerPilot AI.

Provides structured logging with request IDs, execution times,
and proper log levels for all modules.
"""

import logging
import logging.config
import json
import time
from typing import Any, Dict, Optional
from contextlib import contextmanager
import uuid

from app.settings import settings


# ==================== Setup Logging ====================


def setup_logging() -> None:
    """Configure logging for the entire application."""

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.LOG_FORMAT,
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "standard",
                "filename": "logs/careerpilot.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "careerpilot": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            }
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
        },
    }

    # Create logs directory if needed
    import os
    os.makedirs("logs", exist_ok=True)

    logging.config.dictConfig(config)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request ID if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # Add execution time if available
        if hasattr(record, "execution_time_ms"):
            log_data["execution_time_ms"] = record.execution_time_ms

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# ==================== Logger Factory ====================


class LoggerFactory:
    """Factory for creating configured logger instances."""

    _request_id: Optional[str] = None

    @classmethod
    def get_logger(cls, name: str) -> "ContextLogger":
        """Get a logger with context support."""
        return ContextLogger(logging.getLogger(name))

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        """Set current request ID for context logging."""
        cls._request_id = request_id

    @classmethod
    def get_request_id(cls) -> str:
        """Get current request ID or generate a new one."""
        if cls._request_id is None:
            cls._request_id = str(uuid.uuid4())
        return cls._request_id

    @classmethod
    def clear_request_id(cls) -> None:
        """Clear request ID."""
        cls._request_id = None


class ContextLogger:
    """Logger wrapper that adds context information."""

    def __init__(self, logger: logging.Logger):
        """Initialize with a standard logger."""
        self._logger = logger
        self._start_time: Optional[float] = None

    def _add_context(self, record: logging.LogRecord) -> None:
        """Add context info (request ID, execution time) to log record."""
        record.request_id = LoggerFactory.get_request_id()

        if self._start_time is not None:
            elapsed_ms = (time.time() - self._start_time) * 1000
            record.execution_time_ms = f"{elapsed_ms:.2f}"

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log at DEBUG level."""
        record = self._logger.makeRecord(
            self._logger.name,
            logging.DEBUG,
            "dummy.py",
            0,
            msg,
            args,
            exc_info=None,
        )
        self._add_context(record)
        self._logger.handle(record)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log at INFO level."""
        record = self._logger.makeRecord(
            self._logger.name,
            logging.INFO,
            "dummy.py",
            0,
            msg,
            args,
            exc_info=None,
        )
        self._add_context(record)
        self._logger.handle(record)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log at WARNING level."""
        record = self._logger.makeRecord(
            self._logger.name,
            logging.WARNING,
            "dummy.py",
            0,
            msg,
            args,
            exc_info=None,
        )
        self._add_context(record)
        self._logger.handle(record)

    def error(self, msg: str, *args, exc_info=False, **kwargs) -> None:
        """Log at ERROR level."""
        if exc_info and not isinstance(exc_info, Exception):
            # Let the underlying logger handle exc_info properly
            self._logger.error(msg, *args, exc_info=True)
        else:
            record = self._logger.makeRecord(
                self._logger.name,
                logging.ERROR,
                "dummy.py",  # filename
                0,  # line number
                msg,
                args,
                exc_info=exc_info if isinstance(exc_info, Exception) else None
            )
            self._add_context(record)
            self._logger.handle(record)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log at CRITICAL level."""
        record = self._logger.makeRecord(
            self._logger.name,
            logging.CRITICAL,
            "dummy.py",
            0,
            msg,
            args,
            exc_info=None,
        )
        self._add_context(record)
        self._logger.handle(record)

    @contextmanager
    def timer(self, operation: str):
        """Context manager for timing operations."""
        self._start_time = time.time()
        try:
            yield
        finally:
            elapsed_ms = (time.time() - self._start_time) * 1000
            self.info(f"{operation} completed in {elapsed_ms:.2f}ms")
            self._start_time = None


# ==================== Module-level Logger ====================

setup_logging()
logger = LoggerFactory.get_logger("careerpilot")
