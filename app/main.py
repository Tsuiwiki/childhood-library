"""FastAPI application factory (T-05 skeleton).

Run with `uvicorn app.main:create_app --factory`. No module-level app instance
is created, so importing this module for tests has no config/logging side
effects.
"""
from fastapi import FastAPI

from app.api.v1.health import health_router
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import install_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.responses import ok
from app.core.runtime import assert_supported_runtime
from app.schemas.common import ApiResponse


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    assert_supported_runtime()
    setup_logging(settings)

    app = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description="童年书房统一资源管理 API（T-05 骨架，业务能力自 T-06 起）",
        docs_url="/api/docs" if settings.app_env != "production" else None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )
    app.state.settings = settings
    app.add_middleware(RequestContextMiddleware)
    install_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", response_model=ApiResponse, tags=["meta"])
    def root() -> ApiResponse:
        return ok(
            {
                "service": settings.app_name,
                "version": settings.app_version,
                "environment": settings.app_env,
                "docs_url": app.docs_url,
                "api_prefix": settings.api_v1_prefix,
            }
        )

    return app
