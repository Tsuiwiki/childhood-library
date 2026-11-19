"""Alembic environment (T-06).

Connection string policy: read DATABASE_URL from the process environment (or
the repo-root .env via app.core.config.Settings). Never store credentials in
alembic.ini, never echo the URL into logs, and never fall back to a guessed DSN.
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.models import target_metadata  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def database_url() -> str:
    url = get_settings().database_url
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not configured; refusing to guess a database connection"
        )
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(database_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
