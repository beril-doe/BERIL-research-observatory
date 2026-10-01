"""Add content_sha256 to context_ingest_file.

Records the hash of the bytes submitted for each ingested file, so a later
ingest can skip a file whose content already landed. Nullable by design: rows
written before this column existed carry no hash, and a null must never compare
equal to an incoming file — those always re-ingest.

The composite index supports the skip lookup, which filters on relative_path
and status together.

Revision ID: a7b8c9d0e1f2
Revises: f6a1b2c3d4e5
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa

revision = "a7b8c9d0e1f2"
down_revision = "f6a1b2c3d4e5"
branch_labels = None
depends_on = None

_TABLE = "context_ingest_file"
_COLUMN = "content_sha256"
_INDEX = "ix_context_ingest_file_path_status"


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    return bool(
        conn.execute(
            sa.text(
                "SELECT EXISTS ("
                "  SELECT 1 FROM information_schema.columns"
                "  WHERE table_name = :table AND column_name = :column"
                ")"
            ),
            {"table": table, "column": column},
        ).scalar()
    )


def _index_exists(name: str) -> bool:
    conn = op.get_bind()
    return bool(
        conn.execute(
            sa.text(
                "SELECT EXISTS ("
                "  SELECT 1 FROM pg_indexes WHERE indexname = :name"
                ")"
            ),
            {"name": name},
        ).scalar()
    )


def upgrade() -> None:
    # Guarded the same way the table-creating revision is, so a re-run against a
    # partially migrated database is safe.
    if not _column_exists(_TABLE, _COLUMN):
        op.add_column(_TABLE, sa.Column(_COLUMN, sa.String(64), nullable=True))
    if not _index_exists(_INDEX):
        op.create_index(_INDEX, _TABLE, ["relative_path", "status"])


def downgrade() -> None:
    if _index_exists(_INDEX):
        op.drop_index(_INDEX, table_name=_TABLE)
    if _column_exists(_TABLE, _COLUMN):
        op.drop_column(_TABLE, _COLUMN)
