"""API v1 aggregation: seven domain routers."""
from fastapi import APIRouter

from app.api.v1 import catalog, ingestion, media, reviews, rights, sources, versions

DOMAIN_MODULES = (catalog, versions, sources, rights, reviews, media, ingestion)
DOMAIN_NAMES = tuple(module.router.prefix.lstrip("/") for module in DOMAIN_MODULES)

api_router = APIRouter()
for module in DOMAIN_MODULES:
    api_router.include_router(module.router)
