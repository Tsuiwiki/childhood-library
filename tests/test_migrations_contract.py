"""Static contract for the T-06 initial Alembic migration (no DB needed)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def migration_files():
    return sorted(
        path
        for path in (ROOT / "migrations" / "versions").glob("*.py")
        if path.name != "__init__.py"
    )


def test_alembic_layout():
    for relative in (
        "alembic.ini",
        "migrations/env.py",
        "migrations/script.py.mako",
    ):
        assert (ROOT / relative).is_file(), relative
    ini = (ROOT / "alembic.ini").read_text(encoding="utf-8")
    assert "script_location = migrations" in ini
    # Credentials must never live in alembic.ini.
    assert "postgresql+psycopg://" not in ini
    env = (ROOT / "migrations" / "env.py").read_text(encoding="utf-8")
    assert "target_metadata" in env
    assert "DATABASE_URL" in env


def test_single_initial_revision_with_symmetric_downgrade():
    files = migration_files()
    assert len(files) == 1, files
    text = files[0].read_text(encoding="utf-8")
    assert "down_revision: Union[str, None] = None" in text
    assert "def upgrade() -> None:" in text
    assert "def downgrade() -> None:" in text
    assert text.count("op.create_table(") == 20
    assert text.count("op.drop_table(") == 20
    assert "postgresql_nulls_not_distinct=True" in text
    assert "postgresql_where=sa.text('is_primary')" in text


def test_downgrade_drops_dependents_before_parents():
    text = migration_files()[0].read_text(encoding="utf-8")
    downgrade = text.split("def downgrade() -> None:", 1)[1]
    order = {}
    for name in ("playback_resources", "media_assets", "works", "import_batches"):
        order[name] = downgrade.find("op.drop_table('%s')" % name)
        assert order[name] >= 0, name
    assert order["playback_resources"] < order["media_assets"]
    assert order["media_assets"] < order["works"]
    assert order["works"] < order["import_batches"]


def test_migration_contains_no_credentials():
    text = migration_files()[0].read_text(encoding="utf-8")
    for marker in ("change-me", "POSTGRES_PASSWORD", "BEGIN PRIVATE KEY"):
        assert marker not in text
