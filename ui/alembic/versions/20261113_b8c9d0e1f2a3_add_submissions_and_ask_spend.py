"""Add submission, submission_file and ask_spend; add chat_session.mode.

``submission`` records each ``/submit`` as the archive step reports it to
BERIL (``POST /api/context/submissions``), independently of the ingest tables
that track best-effort indexing into the context store; ``submission_file``
is its manifest, with whether BERIL holds each file's bytes. These feed
``GET /api/context/submissions`` and the byte-exact ``/read``.

``ask_spend`` meters the wiki chat mode per user per UTC day (settled and
reserved tokens and USD), and ``chat_session.mode`` tells a wiki session from
a general one; existing sessions are general.

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


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    return bool(
        conn.execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :t)"
            ),
            {"t": name},
        ).scalar()
    )


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    return bool(
        conn.execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.columns"
                " WHERE table_name = :t AND column_name = :c)"
            ),
            {"t": table, "c": column},
        ).scalar()
    )


def upgrade() -> None:
    # Guarded like the earlier context revisions, so a re-run against a
    # partially migrated database is safe.
    if not _table_exists("submission"):
        op.create_table(
            "submission",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "owner_user_id",
                sa.String(36),
                sa.ForeignKey("beril_user.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("owner_orcid", sa.String(64), nullable=False),
            sa.Column("project", sa.String(128), nullable=False),
            sa.Column("revision", sa.String(64), nullable=False),
            sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("archive_path", sa.Text(), nullable=True),
            sa.Column("approval_by", sa.String(64), nullable=True),
            sa.Column("approval_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("kind", sa.String(16), nullable=False, server_default="approved"),
            sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint(
                "owner_orcid", "project", "revision", name="uq_submission_owner_project_revision"
            ),
        )
        op.create_index("ix_submission_owner_user_id", "submission", ["owner_user_id"])
        op.create_index("ix_submission_owner_orcid", "submission", ["owner_orcid"])
        op.create_index("ix_submission_status_submitted", "submission", ["status", "submitted_at"])

    if not _table_exists("submission_file"):
        op.create_table(
            "submission_file",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "submission_id",
                sa.String(36),
                sa.ForeignKey("submission.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("path", sa.Text(), nullable=False),
            sa.Column("sha256", sa.String(64), nullable=False),
            sa.Column("size", sa.BigInteger(), nullable=False),
            sa.Column("stored", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("content_type", sa.String(128), nullable=True),
            sa.UniqueConstraint("submission_id", "path", name="uq_submission_file_path"),
        )
        op.create_index("ix_submission_file_submission_id", "submission_file", ["submission_id"])

    if not _table_exists("ask_spend"):
        op.create_table(
            "ask_spend",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("beril_user.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("day", sa.Date(), nullable=False),
            sa.Column("tokens", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("reserved_tokens", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("reserved_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("reservations", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("user_id", "day", name="uq_ask_spend_user_day"),
        )
        op.create_index("ix_ask_spend_user_id", "ask_spend", ["user_id"])
        op.create_index("ix_ask_spend_day", "ask_spend", ["day"])

    if not _column_exists("chat_session", "mode"):
        op.add_column(
            "chat_session",
            sa.Column("mode", sa.String(16), nullable=False, server_default="general"),
        )


def downgrade() -> None:
    if _column_exists("chat_session", "mode"):
        op.drop_column("chat_session", "mode")
    for table in ("ask_spend", "submission_file", "submission"):
        if _table_exists(table):
            op.drop_table(table)
