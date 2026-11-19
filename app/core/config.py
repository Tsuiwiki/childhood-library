"""Application settings.

Secrets stay in the repo-root .env (git-ignored). ``database_url`` is never
logged and never returned by ``safe_summary``.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "childhood-library"
    app_env: str = "development"
    app_version: str = "0.5.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    log_level: str = "INFO"
    log_json: bool = True
    log_dir: Path | None = Path("var/logs")

    health_check_db: bool = True
    db_tcp_host: str = "127.0.0.1"
    db_tcp_port: int = 55432

    # T-06: opt-in real SQL readiness. Off by default so a local test run
    # without a database (and without SQLAlchemy installed) stays deterministic.
    health_check_sql: bool = False
    db_sql_timeout: float = 0.8

    # Read from T-06 onward (SQLAlchemy / Alembic). Never exposed in logs,
    # never returned by safe_summary, never echoed into a response.
    database_url: str | None = None

    def safe_summary(self) -> dict:
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "app_version": self.app_version,
            "api_v1_prefix": self.api_v1_prefix,
            "log_level": self.log_level,
            "log_json": self.log_json,
            "health_check_db": self.health_check_db,
            "health_check_sql": self.health_check_sql,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
