"""Database helpers (T-06).

Only the dependency-free SQL probe is re-exported here, so importing
``app.db`` never requires SQLAlchemy to be installed.
"""
from app.db.probe import probe_sql

__all__ = ["probe_sql"]
