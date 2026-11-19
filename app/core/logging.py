"""Structured JSON logging (stdout + optional rotating file)."""
import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import Settings
from app.core.context import request_id_var

EXTRA_FIELDS = (
    "request_id",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "error_code",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is None and field == "request_id":
                value = request_id_var.get()
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rid = getattr(record, "request_id", None) or request_id_var.get()
        return (
            f"{self.formatTime(record)} {record.levelname:<8} "
            f"[{rid}] {record.name}: {record.getMessage()}"
        )


def _formatter(settings: Settings) -> logging.Formatter:
    return JsonFormatter() if settings.log_json else TextFormatter()


def setup_logging(settings: Settings) -> None:
    root = logging.getLogger()
    # Remove only handlers installed by an earlier setup_logging call, so test
    # frameworks (caplog) keep theirs.
    for handler in list(root.handlers):
        if getattr(handler, "_cl_owned", False):
            root.removeHandler(handler)

    stream = logging.StreamHandler(sys.stdout)
    stream._cl_owned = True  # type: ignore[attr-defined]
    stream.setFormatter(_formatter(settings))
    root.addHandler(stream)

    if settings.log_dir:
        try:
            log_dir = Path(settings.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler._cl_owned = True  # type: ignore[attr-defined]
            file_handler.setFormatter(_formatter(settings))
            root.addHandler(file_handler)
        except OSError as exc:
            logging.getLogger("app.logging").warning(
                "file logging disabled (%s); stdout logging remains active", exc
            )

    root.setLevel(settings.log_level.upper())
    # We emit our own structured access log; avoid uvicorn's duplicate one.
    logging.getLogger("uvicorn.access").propagate = False
