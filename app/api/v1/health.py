"""Liveness and readiness probes.

`/healthz` reports APPLICATION health only. Dependency state is informational
and never turns a healthy process into HTTP 500 - a cold database must not make
the container restart loop. `/readyz` (T-06) is the strict dependency probe
that may return 503. Neither endpoint ever echoes DATABASE_URL.
"""
import socket

from fastapi import APIRouter, Request

from app.api.v1.router import DOMAIN_NAMES
from app.core.config import Settings
from app.core.errors import ErrorCode, error_response
from app.core.responses import ok
from app.core.runtime import python_version
from app.db import probe_sql
from app.schemas.common import ApiResponse

health_router = APIRouter(tags=["health"])


def probe_tcp(host: str, port: int, timeout: float = 0.3) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "reachable"
    except OSError:
        return "unreachable"


def sql_state(settings: Settings) -> str:
    if not settings.health_check_sql:
        return "disabled"
    return probe_sql(settings.database_url, settings.db_sql_timeout)


@health_router.get("/healthz", response_model=ApiResponse, summary="应用存活检查")
def healthz(request: Request) -> ApiResponse:
    settings: Settings = request.app.state.settings
    db_state = (
        probe_tcp(settings.db_tcp_host, settings.db_tcp_port)
        if settings.health_check_db
        else "disabled"
    )
    return ok(
        {
            "status": "ok",
            "service": settings.app_name,
            "environment": settings.app_env,
            "version": settings.app_version,
            "python_version": python_version(),
            "api_prefix": settings.api_v1_prefix,
            "domains": list(DOMAIN_NAMES),
            "checks": {
                "database_tcp": db_state,
                "database_sql": sql_state(settings),
            },
        }
    )


@health_router.get("/readyz", summary="依赖就绪检查（SQL 可达才 200）")
def readyz(request: Request):
    settings: Settings = request.app.state.settings
    state = sql_state(settings)
    if state != "reachable":
        return error_response(
            ErrorCode.NOT_READY,
            details={"ready": False, "checks": {"database_sql": state}},
        )
    return ok({"ready": True, "checks": {"database_sql": state}})
