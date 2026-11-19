"""Liveness probe.

`/healthz` reports APPLICATION health only. Dependency state is informational
and never turns a healthy process into HTTP 500 - a cold database must not make
the container restart loop. T-06 adds a real SQL readiness check.
"""
import socket

from fastapi import APIRouter, Request

from app.api.v1.router import DOMAIN_NAMES
from app.core.config import Settings
from app.core.responses import ok
from app.core.runtime import python_version
from app.schemas.common import ApiResponse

health_router = APIRouter(tags=["health"])


def probe_tcp(host: str, port: int, timeout: float = 0.3) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "reachable"
    except OSError:
        return "unreachable"


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
            "checks": {"database_tcp": db_state},
        }
    )
