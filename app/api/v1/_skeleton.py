"""Factory for T-05 skeleton routes.

All seven domains are registered so the API contract and OpenAPI schema exist
from day one, but every endpoint explicitly returns 501. No fake rows and no
placeholder demo data: models, tables and real queries arrive in T-06+.
"""
from fastapi import APIRouter, Query

from app.core.errors import AppError, ErrorCode


def make_domain_router(domain: str, description: str) -> APIRouter:
    router = APIRouter(prefix=f"/{domain}", tags=[domain])

    @router.get("", summary=f"{domain} 领域清单（T-05 占位）")
    def list_placeholder(limit: int = Query(20, ge=1, le=100)):
        _ = limit  # validated now; real pagination comes with the domain model
        raise AppError(
            ErrorCode.NOT_IMPLEMENTED,
            message=f"{domain}: {description}；业务实现从 T-06 起落地",
            details={"domain": domain, "planned_from": "T-06"},
        )

    return router
