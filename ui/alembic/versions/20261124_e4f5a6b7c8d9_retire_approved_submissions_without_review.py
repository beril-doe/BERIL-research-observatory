"""Retire approved submissions recorded without their REVIEW.md.

An approved submission is complete only once its REVIEW.md is stored (the
review its approval's review_hash names, checked against the bundled
bytes). Records made before that rule may be complete without one; this
puts them back to pending and takes them out of the feed (``feed_seq``
cleared — the feed pages by position, so a gap is harmless). They return
only through a re-post that passes the approval check: the post route lets
a re-post of an approved record add the REVIEW.md it lacks, checked
against the recorded beril.yaml's review_hash, and the record then
completes with a new feed position. A consumer that read one before the
upgrade keeps what it read: the feed has no retraction.

Revision ID: e4f5a6b7c8d9
Revises: d2e3f4a5b6c7
Create Date: 2026-11-24
"""

from alembic import op

revision = "e4f5a6b7c8d9"
down_revision = "d2e3f4a5b6c7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE submission
        SET status = 'pending', feed_seq = NULL
        WHERE kind = 'approved'
          AND status = 'complete'
          AND NOT EXISTS (
              SELECT 1 FROM submission_file AS f
              WHERE f.submission_id = submission.id
                AND f.path = 'REVIEW.md'
                AND f.stored
          )
        """
    )


def downgrade() -> None:
    # Which rows were retired is not recorded, and they should stay out.
    pass
