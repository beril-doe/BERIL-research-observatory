"""Add submission.feed_seq: each submission's place in the feed.

The feed paged by ``submitted_at``, which the archive step supplies and which
does not move when a submission completes, so a submission completing after a
later one had been fed fell behind every cursor already issued. ``feed_seq``
is given when a submission completes, in commit order, and the feed pages by
it. Submissions already complete are numbered in their old feed order.

Revision ID: c0d1e2f3a4b5
Revises: b8c9d0e1f2a3
Create Date: 2026-11-18
"""

from alembic import op
import sqlalchemy as sa

revision = "c0d1e2f3a4b5"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


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
    if _column_exists("submission", "feed_seq"):
        return
    op.add_column("submission", sa.Column("feed_seq", sa.BigInteger(), nullable=True))
    op.execute(
        """
        UPDATE submission AS s
        SET feed_seq = n.seq
        FROM (
            SELECT id, row_number() OVER (ORDER BY submitted_at, id) AS seq
            FROM submission
            WHERE status = 'complete'
        ) AS n
        WHERE s.id = n.id
        """
    )
    op.create_index("ix_submission_feed_seq", "submission", ["feed_seq"], unique=True)


def downgrade() -> None:
    if _column_exists("submission", "feed_seq"):
        op.drop_index("ix_submission_feed_seq", table_name="submission")
        op.drop_column("submission", "feed_seq")
