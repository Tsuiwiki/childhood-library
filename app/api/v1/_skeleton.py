"""Factory for the seven placeholder domain routes (T-05 skeleton).

Every endpoint explicitly returns 501: no fake rows, no placeholder demo data.
T-06 landed the schema, but real queries and business commands are wired from
T-07 onward, domain by domain - so the payload must not claim T-06 implements
business behaviour.
"""
from fastapi import APIRouter, Query

from app.core.errors import AppError, ErrorCode


def make_domain_router(domain: str, description: str) -> APIRouter:
    router = APIRouter(prefix=f"/{domain}", tags=[domain])

    @router.get("", summary=f"{domain} 领域清单（占位）")
    def list_placeholder(limit: int = Query(20, ge=1, le=100)):
        _ = limit  # validated now; real pagination comes with the domain model
        raise AppError(
            ErrorCode.NOT_IMPLEMENTED,
            message=f"{domain}: {description}；数据层（T-06）已就绪，业务实现待后续任务",
            details={"domain": domain, "planned_from": "post-T-06"},
        )

    return router
