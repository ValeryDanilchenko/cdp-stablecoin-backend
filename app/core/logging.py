import logging
import logging.config
from typing import Any

from app.core.config import settings
from app.core.request_id import RequestIdFilter


def configure_logging() -> None:
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
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "filters": ["request_id"],
            }
        },
        "root": {"handlers": ["default"], "level": level},
    }
    logging.config.dictConfig(config)
