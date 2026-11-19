"""T-06 ORM metadata contract. Skipped when the DB stack is unavailable."""
import pytest

pytest.importorskip("sqlalchemy", reason="T-06 DB dependencies required")

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint  # noqa: E402

from app.models import ALL_TABLES, CORE_ENTITIES, Base, Work  # noqa: E402
from app.models.enums import (  # noqa: E402
    DB_ENUMS,
    STATUS_DIMENSION_COLUMNS,
    enum_values,
    in_check,
)


def test_core_entities_and_support_tables():
    assert len(CORE_ENTITIES) == 10
    assert len(ALL_TABLES) == 20
    assert set(Base.metadata.tables) == set(ALL_TABLES)
    for name in CORE_ENTITIES:
        assert name in Base.metadata.tables


def test_five_status_dimensions_are_separate_columns():
    columns = set(Work.__table__.columns.keys())
    for name in STATUS_DIMENSION_COLUMNS:
        assert name in columns
    assert len(STATUS_DIMENSION_COLUMNS) == 5
    checks = {
        constraint.name
        for constraint in Work.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    for name in STATUS_DIMENSION_COLUMNS:
        assert name in checks, "missing CHECK for %s" % name


def test_enum_checks_cover_every_value():
    for enum_cls in DB_ENUMS:
        values = enum_values(enum_cls)
        assert values
        assert len(values) == len(set(values))
        expression = in_check("col", enum_cls)
        for value in values:
            assert "'%s'" % value in expression


def test_constraints_and_foreign_keys_are_present():
    checks = fks = uniques = 0
    for table in Base.metadata.tables.values():
        checks += sum(
            isinstance(c, CheckConstraint) for c in table.constraints
        )
        uniques += sum(
            isinstance(c, UniqueConstraint) for c in table.constraints
        )
        fks += len(table.foreign_keys)
    assert checks >= 45, checks
    assert uniques >= 10, uniques
    assert fks >= 30, fks


def test_foreign_keys_all_resolve():
    names = set(Base.metadata.tables)
    for table in Base.metadata.tables.values():
        for fk in table.foreign_keys:
            assert fk.target_fullname.split(".")[0] in names


def test_dependency_order_has_no_cycle():
    assert len(list(Base.metadata.sorted_tables)) == len(ALL_TABLES)


def test_nulls_not_distinct_unique_constraints():
    names = set()
    for table in Base.metadata.tables.values():
        for constraint in table.constraints:
            if isinstance(constraint, UniqueConstraint):
                dialect = constraint.dialect_options.get("postgresql", {})
                if dialect.get("nulls_not_distinct"):
                    names.add(constraint.name)
    assert len(names) >= 5, names
