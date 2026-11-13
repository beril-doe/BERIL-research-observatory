"""Add kind to context_ingest_batch.

Records how each batch came to exist — ``approved`` (a ``/submit`` ingest),
``seeded`` (an admin import of a repo project that predates ``/submit``) or
``retirement`` (an import's bookkeeping for a re-owned project's old copies) —
so the submissions feed (``GET /api/context/submissions``) can tell a reviewed
submission from a seeded one.

Every row written before this column existed came from ``/ingest_files`` or
an admin import; the import route could not say which, so all are backfilled
as ``approved``, which is also the server default. Admin imports from this
revision on write ``seeded``.

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-11-13
"""

from alembic import op
import sqlalchemy as sa

revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None

_TABLE = "context_ingest_batch"
_COLUMN = "kind"
_INDEX = "ix_context_ingest_batch_kind_created"


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
            sa.text("SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = :name)"),
            {"name": name},
        ).scalar()
    )


def upgrade() -> None:
    # Guarded like the earlier context_ingest revisions, so a re-run against a
    # partially migrated database is safe. The server default backfills every
    # existing row as ``approved`` in the same statement.
    if not _column_exists(_TABLE, _COLUMN):
        op.add_column(
            _TABLE,
            sa.Column(_COLUMN, sa.String(16), nullable=False, server_default="approved"),
        )
    # The feed filters on kind and pages by created_at.
    if not _index_exists(_INDEX):
        op.create_index(_INDEX, _TABLE, [_COLUMN, "created_at"])


def downgrade() -> None:
    if _index_exists(_INDEX):
        op.drop_index(_INDEX, table_name=_TABLE)
    if _column_exists(_TABLE, _COLUMN):
        op.drop_column(_TABLE, _COLUMN)
