"""media 领域路由（T-05 骨架 + T-07 能力状态）。

The domain LIST endpoint is still a 501 placeholder: full media CRUD belongs to
T-09 / T-10 per IMPLEMENTATION_ROADMAP.md. T-07 adds one read-only capability
endpoint so the landed provider/gate can be observed without touching the
business tables. It never returns a URL and never exposes credentials.
"""
from fastapi import Request

from app.api.v1._skeleton import make_domain_router
from app.core.config import Settings
from app.core.responses import ok
from app.media.local import LocalStorageAdapter

router = make_domain_router("media", "媒体资产元数据、存储与访问方式")


@router.get("/capabilities", summary="T-07 媒体能力状态（不返回任何访问 URL）")
def capabilities(request: Request):
    settings: Settings = request.app.state.settings
    root = settings.resolved_media_root()
    provider = LocalStorageAdapter(
        root,
        read_only=settings.media_read_only,
        max_object_bytes=settings.media_max_object_bytes,
    )
    flat_objects = (
        sum(1 for item in root.iterdir() if item.is_file()) if root.is_dir() else 0
    )
    return ok(
        {
            "stage": "T-07 / M0 local adapter",
            "provider": provider.name,
            "root_exists": root.is_dir(),
            "read_only": provider.read_only,
            "flat_object_count": flat_objects,
            "operations": ["put", "get", "stat", "delete", "range", "checksum"],
            "rights_gate": [
                "research_metadata",
                "internal_content",
                "public_url",
            ],
            "public_url_issued": False,
            "note": (
                "object_key is an internal key, not a URL; rights unknown never "
                "blocks research registration and never yields a public address"
            ),
        }
    )
