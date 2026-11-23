"""Widen submission_file.size to BIGINT.

The manifest lists every archived file, datasets included, so a size can
pass the 2 GiB a 32-bit INTEGER holds; recording such a submission failed.
b8c9d0e1f2a3 now creates the column as BIGINT; this widens it where that
revision already ran with INTEGER.

Revision ID: d2e3f4a5b6c7
Revises: c0d1e2f3a4b5
Create Date: 2026-11-23
"""

import sqlalchemy as sa

from alembic import op

revision = "d2e3f4a5b6c7"
down_revision = "c0d1e2f3a4b5"
branch_labels = None
depends_on = None


def _size_type() -> str | None:
    conn = op.get_bind()
    return conn.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns"
            " WHERE table_name = 'submission_file' AND column_name = 'size'"
        )
    ).scalar()


def upgrade() -> None:
    if _size_type() == "integer":
        op.alter_column(
            "submission_file", "size", existing_type=sa.Integer(), type_=sa.BigInteger(),
            existing_nullable=False,
        )


def downgrade() -> None:
    # Narrowing would fail on any size past 2 GiB, and b8c9d0e1f2a3 now
    # creates the column as BIGINT, so the downgrade leaves it wide.
    pass
