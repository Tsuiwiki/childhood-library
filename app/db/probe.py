"""Short-timeout SQL readiness probe.

SQLAlchemy is imported lazily: a local static run without the DB stack can
still import the API package. The connection string is never logged; only the
exception class name is recorded at DEBUG level.
"""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger("app.db.probe")


@lru_cache(maxsize=4)
def _engine(url: str, timeout_seconds: int):
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    return create_engine(
        url,
        poolclass=NullPool,
        connect_args={"connect_timeout": timeout_seconds},
    )


def probe_sql(url: str | None, timeout: float = 0.8) -> str:
    """Return one of: reachable / unreachable / not_configured / unavailable."""
    if not url:
        return "not_configured"
    try:
        from sqlalchemy import text
    except ImportError:
        return "unavailable"
    try:
        engine = _engine(url, max(1, int(timeout)))
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "reachable"
    except Exception as exc:  # noqa: BLE001 - dependency state is informational
        logger.debug("sql readiness probe failed: %s", type(exc).__name__)
        return "unreachable"
