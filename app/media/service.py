"""MediaAssetService - register bytes into the T-06 schema.

SQLAlchemy is imported ONLY in this module. ``app/media/__init__.py`` does not
import it, so provider / probe / integrity / rights_gate stay usable without a
database or SQLAlchemy installed (the same lazy-import rule as app/db/probe.py).

Hard rules (PROJECT_PRINCIPLES.md, MEDIA_ASSET_DESIGN.md section 8):
* registering a file NEVER creates a PlaybackResource or a public address;
* rights_status stays ``unknown`` and publication_status stays ``draft``;
* object_key is a provider-neutral key, never a vendor URL;
* delete / replace writes an AuditLog entry.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.status import PublicationStatus, RightsStatus
from app.media.integrity import sha256_path, verify_object
from app.media.probe import MediaProbe, probe_file
from app.media.provider import StorageProvider
from app.models.enums import AssetRole, MediaType, enum_values
from app.models.media import MediaAsset, StorageLocation
from app.models.rights import RightsRecord
from app.models.support import AuditLog

KEY_PREFIX = {
    MediaType.AUDIO.value: "childhood-library/audio/music",
    MediaType.IMAGE.value: "childhood-library/images/covers",
    MediaType.SCORE_XML.value: "childhood-library/scores",
    MediaType.DOCUMENT.value: "childhood-library/scores",
    MediaType.VIDEO.value: "childhood-library/audio/music",
    MediaType.OTHER.value: "childhood-library/attachments",
}


class UnknownMediaFormat(Exception):
    """File signature could not be identified; registration refused."""


class MediaAssetService:
    def __init__(
        self,
        provider: StorageProvider,
        session: Session,
        *,
        actor: str = "system",
    ) -> None:
        self.provider = provider
        self.session = session
        self.actor = actor

    @staticmethod
    def object_key_for(
        asset_id: uuid.UUID, probe: MediaProbe, work_id: uuid.UUID | None = None
    ) -> str:
        prefix = KEY_PREFIX.get(probe.media_type, KEY_PREFIX[MediaType.OTHER.value])
        folder = str(work_id) if work_id else "general"
        extension = probe.file_extension or ".bin"
        return "%s/%s/%s%s" % (prefix, folder, asset_id, extension)

    def _pair(self, asset_id: uuid.UUID) -> tuple[MediaAsset, StorageLocation | None]:
        asset = self.session.get(MediaAsset, asset_id)
        if asset is None:
            raise KeyError(str(asset_id))
        location = self.session.scalar(
            select(StorageLocation).where(StorageLocation.asset_id == asset_id)
        )
        return asset, location

    @staticmethod
    def view(asset: MediaAsset, location: StorageLocation | None = None) -> dict:
        """DTO without ANY URL. object_key is an internal storage key only."""
        return {
            "asset_id": str(asset.asset_id),
            "asset_role": asset.asset_role,
            "media_type": asset.media_type,
            "mime_type": asset.mime_type,
            "file_extension": asset.file_extension,
            "file_size_bytes": asset.file_size_bytes,
            "duration_ms": asset.duration_ms,
            "checksum_sha256": asset.checksum_sha256,
            "rights_status": asset.rights_status,
            "publication_status": asset.publication_status,
            "rights_record_id": (
                str(asset.rights_record_id) if asset.rights_record_id else None
            ),
            "storage_provider": location.provider if location else None,
            "object_key": location.object_key if location else None,
            "object_key_note": "internal provider key, NOT an access URL",
        }

    def register(
        self,
        source: Path | str,
        *,
        asset_role: str = AssetRole.RECORDING.value,
        work_id: uuid.UUID | None = None,
        rights_record_id: uuid.UUID | None = None,
        duration_ms: int | None = None,
        storage_note: str | None = None,
        allow_unknown_format: bool = False,
    ) -> dict:
        src = Path(source)
        if not src.is_file():
            raise FileNotFoundError(str(src))
        if asset_role not in enum_values(AssetRole):
            raise ValueError("asset_role not in the T-06 value set: %s" % asset_role)

        probe = probe_file(src, duration_ms_override=duration_ms)
        if probe.mime_type is None and not allow_unknown_format:
            raise UnknownMediaFormat(
                "file signature not recognised: %s (pass allow_unknown_format=True "
                "only for a reviewed generic attachment)" % src.name
            )
        if rights_record_id is not None:
            found = self.session.get(RightsRecord, rights_record_id)
            if found is None:
                raise KeyError("rights_record_id %s does not exist" % rights_record_id)

        asset_id = uuid.uuid4()
        object_key = self.object_key_for(asset_id, probe, work_id)
        expected = sha256_path(src)
        stat = self.provider.put(object_key, src, expected_sha256=expected)

        now = datetime.now(timezone.utc)
        asset = MediaAsset(
            asset_id=asset_id,
            work_id=work_id,
            rights_record_id=rights_record_id,
            asset_role=asset_role,
            media_type=probe.media_type,
            mime_type=probe.mime_type,
            file_extension=probe.file_extension,
            file_size_bytes=stat.size_bytes,
            duration_ms=probe.duration_ms,
            checksum_sha256=stat.checksum_sha256,
            rights_status=RightsStatus.UNKNOWN.value,
            publication_status=PublicationStatus.DRAFT.value,
            storage_note=storage_note,
            metadata_={
                "duration_probe": probe.duration_probe,
                "signature_detected": probe.mime_type is not None,
                "source_filename": src.name,
                "registered_by": "T-07 MediaAssetService",
            },
        )
        location = StorageLocation(
            asset_id=asset_id,
            provider=self.provider.name,
            object_key=object_key,
            is_primary=True,
            byte_size=stat.size_bytes,
            checksum_sha256=stat.checksum_sha256,
            verified_at=now,
        )
        self.session.add_all([asset, location])
        self.session.add(
            AuditLog(
                entity_type="media_asset",
                entity_id=asset_id,
                action="register",
                actor=self.actor,
                after={"object_key": object_key, "checksum_sha256": stat.checksum_sha256},
            )
        )
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            try:
                self.provider.delete(object_key)
            except Exception:
                pass  # never mask the original database error
            raise
        return self.view(asset, location)

    def describe(self, asset_id: uuid.UUID) -> dict:
        asset, location = self._pair(asset_id)
        return self.view(asset, location)

    def list_assets(self, *, limit: int = 20, offset: int = 0) -> list[dict]:
        rows = self.session.scalars(
            select(MediaAsset)
            .order_by(MediaAsset.created_at)
            .limit(max(1, min(limit, 100)))
            .offset(max(0, offset))
        ).all()
        return [self.view(row) for row in rows]

    def verify(self, asset_id: uuid.UUID) -> dict:
        asset, location = self._pair(asset_id)
        if location is None or not location.object_key:
            return {
                "object_key": None,
                "expected": asset.checksum_sha256,
                "actual": None,
                "ok": False,
                "message": "no storage location recorded",
            }
        return verify_object(
            self.provider, location.object_key, asset.checksum_sha256
        ).as_dict()

    def delete(self, asset_id: uuid.UUID) -> dict:
        asset, location = self._pair(asset_id)
        before: dict[str, Any] = self.view(asset, location)
        removed = False
        if location and location.object_key:
            removed = self.provider.delete(location.object_key)
        self.session.delete(asset)  # cascades to storage_locations
        self.session.add(
            AuditLog(
                entity_type="media_asset",
                entity_id=asset_id,
                action="delete",
                actor=self.actor,
                before=before,
            )
        )
        self.session.commit()
        return {"asset_id": str(asset_id), "object_removed": removed, "deleted": True}
