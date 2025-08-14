"""Structured JSON logging utilities.

Centralized configuration so all modules log consistent machine-parseable
events. Keep very lightweight to avoid import overhead.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            payload.update(record.extra_data)
        return json.dumps(payload, ensure_ascii=False)


def configure_json_logging(level: str | int = "INFO") -> None:
    """Configure root logger to emit JSON to stdout."""
    if isinstance(level, str):
        level_value = getattr(logging, level.upper(), logging.INFO)
    else:
        level_value = level

    root = logging.getLogger()
    root.setLevel(level_value)
    # Clear existing handlers to avoid duplicates in notebooks/REPL
    root.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def log_event(logger: logging.Logger, message: str, **extra: Any) -> None:
    """Log a structured event at INFO level."""
    logger.info(message, extra={"extra_data": extra})


