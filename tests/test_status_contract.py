"""Five status dimensions stay independent (T-06 must not collapse them)."""
from app.core.errors import ErrorCode
from app.domain.status import (
    STATUS_DIMENSIONS,
    AccessMethod,
    PublicationStatus,
    QualityStatus,
    ResearchStatus,
    RightsStatus,
)


def values(enum_cls):
    return {member.value for member in enum_cls}


def test_five_dimensions_are_independent():
    assert set(STATUS_DIMENSIONS) == {
        "research_status",
        "rights_status",
        "quality_status",
        "access_method",
        "publication_status",
    }
    assert len(STATUS_DIMENSIONS) == 5


def test_status_values_match_project_principles():
    assert values(ResearchStatus) == {
        "discovered", "researching", "reviewed", "rejected",
    }
    assert values(RightsStatus) == {
        "unknown", "pending", "verified", "restricted", "revoked",
    }
    assert values(QualityStatus) == {
        "unreviewed", "suitable", "needs_context", "unsuitable",
    }
    assert values(AccessMethod) == {
        "none", "source_link", "official_embed", "licensed_media", "own_original",
    }
    assert values(PublicationStatus) == {
        "draft", "pending_review", "approved", "published", "withdrawn",
    }


def test_error_codes_cover_skeleton_contract():
    assert {code.value for code in ErrorCode} >= {
        "OK",
        "VALIDATION_ERROR",
        "NOT_FOUND",
        "METHOD_NOT_ALLOWED",
        "NOT_IMPLEMENTED",
        "INTERNAL_ERROR",
    }
