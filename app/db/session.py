"""Engine / Session factories for T-07+ application code.

Not imported by the liveness endpoints: importing this module requires
SQLAlchemy. Alembic reads DATABASE_URL directly in migrations/env.py and does
not use this factory, so a migration can run before the API is ready.
"""
from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache(maxsize=4)
def get_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def session_factory() -> sessionmaker[Session]:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return sessionmaker(
        bind=get_engine(settings.database_url),
        expire_on_commit=False,
        autoflush=False,
    )
