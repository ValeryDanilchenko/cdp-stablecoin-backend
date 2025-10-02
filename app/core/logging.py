import json
import logging
import logging.config
from typing import Any

from app.core.config import settings
from app.core.request_id import RequestIdFilter


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def configure_logging() -> None:
    """Configure structured logging for the application."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {
                "()": RequestIdFilter,
            }
        },
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)s %(name)s [%(request_id)s] - %(message)s",
            },
            "json": {
                "()": JSONFormatter,
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "json" if settings.log_format == "json" else "standard",
                "level": level,
                "filters": ["request_id"],
            }
        },
        "loggers": {
            "app": {
                "handlers": ["default"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {"handlers": ["default"], "level": level},
    }
    logging.config.dictConfig(config)
