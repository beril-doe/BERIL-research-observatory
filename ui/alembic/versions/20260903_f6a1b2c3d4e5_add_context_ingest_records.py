"""Add context_ingest_batch and context_ingest_file tables.

Records each context-manager ingest submission so its progress can be polled
after the request returns. The backing context manager expires its own task
records (24h completed / 7d failed) and does not record who owns them, so
BERIL keeps its own copy for both durability and authorization.

Revision ID: f6a1b2c3d4e5
Revises: e5f6a1b2c3d4
Create Date: 2026-09-03
"""

from alembic import op
import sqlalchemy as sa

revision = "f6a1b2c3d4e5"
down_revision = "e5f6a1b2c3d4"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_name = :name"
            ")"
        ),
        {"name": name},
    )
    return result.scalar()


def upgrade() -> None:
    if not _table_exists("context_ingest_batch"):
        op.create_table(
            "context_ingest_batch",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("beril_user.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "project_id",
                sa.String(36),
                sa.ForeignKey("user_project.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("target_root", sa.Text, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(
            "ix_context_ingest_batch_user_id", "context_ingest_batch", ["user_id"]
        )
        op.create_index(
            "ix_context_ingest_batch_project_id", "context_ingest_batch", ["project_id"]
        )

    if not _table_exists("context_ingest_file"):
        op.create_table(
            "context_ingest_file",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "batch_id",
                sa.String(36),
                sa.ForeignKey("context_ingest_batch.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("relative_path", sa.Text, nullable=False),
            sa.Column("uri", sa.Text, nullable=True),
            sa.Column("ov_task_id", sa.String(128), nullable=True),
            sa.Column("status", sa.String(32), nullable=False),
            sa.Column("error", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(
            "ix_context_ingest_file_batch_id", "context_ingest_file", ["batch_id"]
        )


def downgrade() -> None:
    op.drop_table("context_ingest_file")
    op.drop_table("context_ingest_batch")
