"""The rules of a submission record: its manifest, which files the wiki
needs, when it is complete, and the store-first read.

Kept out of the routes so the admin import and ``/read`` share them.
"""

from __future__ import annotations

import asyncio
import hashlib
import mimetypes
import re
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.context_manager.base import (
    READABLE_FIGURES_DIR,
    ContextFile,
    ContextFileNotFound,
    is_readable_path,
)
from app.db.models import Submission, SubmissionFile
from app.submissions.store import SubmissionStore

# Where a file's bytes came from when the submission store answered.
FILE_SOURCE_SUBMISSION = "submission"

SUBMISSION_PENDING = "pending"
SUBMISSION_COMPLETE = "complete"

KIND_APPROVED = "approved"
KIND_SEEDED = "seeded"
KIND_DOCS = "docs"
SUBMISSION_KINDS = (KIND_APPROVED, KIND_SEEDED, KIND_DOCS)

# The house account's central digests, fed as ``kind: docs`` under
# owner ``beril``, project ``docs``.
DOCS_OWNER = "beril"
DOCS_PROJECT = "docs"
DOCS_FILES = frozenset({"discoveries.md", "pitfalls.md", "performance.md", "research_ideas.md"})

_SHA256 = re.compile(r"[0-9a-f]{64}")
# A figure the report embeds: markdown ``![alt](figures/x.png)`` or an HTML
# ``<img src="figures/x.png">``; a query string or fragment after the path is
# dropped. Relative paths only — a URL is not a project file.
_EMBED = re.compile(
    r"""!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)|<img\b[^>]*?\bsrc\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)


def embedded_figures(report: str) -> set[str]:
    """Paths under ``figures/`` that ``REPORT.md`` embeds, normalized to the
    project-relative form the manifest uses (``./`` and ``?``/``#`` tails
    dropped)."""
    found: set[str] = set()
    for match in _EMBED.finditer(report):
        target = (match.group(1) or match.group(2) or "").strip()
        target = target.split("?", 1)[0].split("#", 1)[0]
        if target.startswith("./"):
            target = target[2:]
        if target.startswith(READABLE_FIGURES_DIR) and is_readable_path(target):
            found.add(target)
    return found


class ManifestFile(BaseModel):
    path: str = Field(min_length=1)
    sha256: str
    size: int = Field(ge=0)

    @field_validator("sha256")
    @classmethod
    def _hex(cls, value: str) -> str:
        value = value.strip().lower().removeprefix("sha256:")
        if not _SHA256.fullmatch(value):
            raise ValueError("not a sha256 hex digest")
        return value


class ManifestApproval(BaseModel):
    by: str = Field(min_length=1)
    at: datetime | None = None
    report_hash: str | None = None

    @field_validator("report_hash")
    @classmethod
    def _hex(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower().removeprefix("sha256:")
        if not _SHA256.fullmatch(value):
            raise ValueError("not a sha256 hex digest")
        return value


class SubmissionManifest(BaseModel):
    """``manifest.json`` as the archive step writes it."""

    project: str = Field(min_length=1)
    owner_orcid: str = Field(min_length=1)
    revision: str
    submitted_at: datetime
    archive_path: str | None = None
    approval: ManifestApproval
    files: list[ManifestFile]

    @field_validator("revision")
    @classmethod
    def _hex(cls, value: str) -> str:
        value = value.strip().lower().removeprefix("sha256:")
        if not _SHA256.fullmatch(value):
            raise ValueError("revision must be the sha256 hex digest of REPORT.md")
        return value

    @field_validator("files")
    @classmethod
    def _unique_paths(cls, files: list[ManifestFile]) -> list[ManifestFile]:
        paths = [f.path for f in files]
        if len(paths) != len(set(paths)):
            raise ValueError("manifest lists a path twice")
        if "REPORT.md" not in paths:
            raise ValueError("manifest must list REPORT.md")
        return files

    @field_validator("submitted_at")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def required_paths(manifest_paths: list[str], report: str | None) -> set[str]:
    """The manifest paths the wiki needs stored before a submission is
    complete: every readable text file the manifest lists, plus the figures
    the report embeds. A figure the report does not embed may still be
    stored, but is not waited for. Without the report's text (not stored
    yet) no figure is required yet."""
    text = {
        p for p in manifest_paths
        if (is_readable_path(p) and not p.startswith(READABLE_FIGURES_DIR)) or p in DOCS_FILES
    }
    if report is None:
        return text
    figures = embedded_figures(report) & set(manifest_paths)
    return text | figures


def compute_status(submission: Submission, report: str | None) -> str:
    stored = {f.path for f in submission.files if f.stored}
    needed = required_paths([f.path for f in submission.files], report)
    return SUBMISSION_COMPLETE if needed <= stored else SUBMISSION_PENDING


def missing_paths(submission: Submission, report: str | None) -> list[str]:
    stored = {f.path for f in submission.files if f.stored}
    return sorted(required_paths([f.path for f in submission.files], report) - stored)


def aware(value: datetime | None) -> datetime | None:
    """A stored timestamp as UTC-aware. SQLite hands back naive datetimes
    (they were written as UTC); Postgres hands back aware ones."""
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=timezone.utc)


def content_type_for(path: str) -> str | None:
    return mimetypes.guess_type(path)[0]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def get_submission(
    db: AsyncSession, submission_id: str, *, for_update: bool = False
) -> Submission | None:
    """The submission with its files. ``for_update`` row-locks it until the
    transaction ends (Postgres; SQLite serializes writers anyway) and
    re-reads everything, so the caller sees what the last holder committed."""
    query = (
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.files))
    )
    if for_update:
        query = query.with_for_update(of=Submission).execution_options(populate_existing=True)
    return (await db.execute(query)).scalar_one_or_none()


async def find_submission(
    db: AsyncSession, *, owner_orcid: str, project: str, revision: str
) -> Submission | None:
    return (
        await db.execute(
            select(Submission)
            .where(
                Submission.owner_orcid == owner_orcid,
                Submission.project == project,
                Submission.revision == revision,
            )
            .options(selectinload(Submission.files))
        )
    ).scalar_one_or_none()


async def latest_complete_submission(
    db: AsyncSession, *, owner_orcid: str, project: str, revision: str | None = None
) -> Submission | None:
    """The newest complete submission of ``project`` — or the one at
    ``revision``, complete or not, when named."""
    query = (
        select(Submission)
        .where(Submission.owner_orcid == owner_orcid, Submission.project == project)
        .options(selectinload(Submission.files))
    )
    if revision is not None:
        query = query.where(Submission.revision == revision)
    else:
        query = query.where(Submission.status == SUBMISSION_COMPLETE)
    query = query.order_by(Submission.submitted_at.desc(), Submission.id.desc()).limit(1)
    return (await db.execute(query)).scalar_one_or_none()


async def complete_submissions_after(
    db: AsyncSession, *, after: int | None, kinds: tuple[str, ...], limit: int
) -> list[Submission]:
    """Complete submissions of the given kinds whose ``feed_seq`` is past
    ``after`` (exclusive), in feed order, at most ``limit``, files loaded."""
    query = (
        select(Submission)
        .where(
            Submission.status == SUBMISSION_COMPLETE,
            Submission.feed_seq.is_not(None),
            Submission.kind.in_(kinds),
        )
        .options(selectinload(Submission.files))
        .order_by(Submission.feed_seq)
        .limit(limit)
    )
    if after is not None:
        query = query.where(Submission.feed_seq > after)
    return list((await db.execute(query)).scalars())


async def complete_submissions_since(
    db: AsyncSession, *, since: datetime | None, kinds: tuple[str, ...], limit: int
) -> list[Submission]:
    """Complete submissions of the given kinds after ``since`` (exclusive),
    oldest first, at most ``limit``, files loaded. The feed's deprecated
    ``since`` mode: a submission completing after a later one was fed is
    never seen again; page by :func:`complete_submissions_after` instead."""
    query = (
        select(Submission)
        .where(Submission.status == SUBMISSION_COMPLETE, Submission.kind.in_(kinds))
        .options(selectinload(Submission.files))
        .order_by(Submission.submitted_at, Submission.id)
        .limit(limit)
    )
    if since is not None:
        query = query.where(Submission.submitted_at > since)
    return list((await db.execute(query)).scalars())


async def store_file(
    store: SubmissionStore, submission: Submission, record: SubmissionFile, data: bytes
) -> None:
    """Write one manifest file's bytes and mark it stored. The caller has
    already checked the hash."""
    await asyncio.to_thread(
        store.put, submission.owner_orcid, submission.project, submission.revision, record.path, data
    )
    record.stored = True
    if record.content_type is None:
        record.content_type = content_type_for(record.path)


async def report_text(store: SubmissionStore, submission: Submission) -> str | None:
    """The stored REPORT.md as text, or None when it is not stored yet."""
    report = next((f for f in submission.files if f.path == "REPORT.md" and f.stored), None)
    if report is None:
        return None
    data = await asyncio.to_thread(
        store.get, submission.owner_orcid, submission.project, submission.revision, "REPORT.md"
    )
    return data.decode("utf-8", errors="replace")


# Key of the advisory lock that orders feed_seq ("SUBFEED" as a 64-bit int).
_FEED_LOCK_KEY = 0x0053554246454544


async def refresh_status(db: AsyncSession, store: SubmissionStore, submission: Submission) -> str:
    """Recompute ``status``; on completion, give the submission its place in
    the feed.

    ``feed_seq`` is the next number under a transaction-scoped lock, so it is
    handed out in commit order: a reader that sees ``n`` committed can rely
    on every lower number being committed too, and a cursor never passes a
    row still to come. The caller commits straight after; nothing slow may
    run between this and the commit (the lock is held until then).

    Lock order: the caller already holds the submission's row (its own new
    insert, or ``get_submission(..., for_update=True)``), and only then is
    the feed lock taken here. Every path takes them in that order, so a
    holder of the feed lock never waits on a row lock.
    """
    submission.status = compute_status(submission, await report_text(store, submission))
    if submission.status == SUBMISSION_COMPLETE and submission.feed_seq is None:
        if db.get_bind().dialect.name == "postgresql":
            await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": _FEED_LOCK_KEY})
        top = (await db.execute(select(func.max(Submission.feed_seq)))).scalar_one()
        submission.feed_seq = (top or 0) + 1
    return submission.status


async def read_submission_file(
    db: AsyncSession,
    store: SubmissionStore,
    *,
    owner: str,
    project: str,
    path: str,
    revision: str | None = None,
) -> ContextFile | None:
    """The file from the submission store — byte-exact by construction —
    or ``None`` when no submission holds it (so the caller may fall back).

    With ``revision`` the exact revision is read, complete or not; without
    it, the newest complete one. Raises ``ContextFileNotFound`` when a
    revision was named and does not have the file: there is nothing older
    to fall back to that would still be that revision.
    """
    submission = await latest_complete_submission(
        db, owner_orcid=owner, project=project, revision=revision
    )
    if submission is None:
        if revision is not None:
            raise ContextFileNotFound(f"{owner}/{project}@{revision}")
        return None
    record = next((f for f in submission.files if f.path == path and f.stored), None)
    if record is None:
        if revision is not None:
            raise ContextFileNotFound(f"{owner}/{project}@{revision}/{path}")
        return None
    data = await asyncio.to_thread(store.get, owner, project, submission.revision, path)
    return ContextFile.from_bytes(
        data,
        address=f"{owner}/{project}/{path}",
        owner=owner,
        project=project,
        path=path,
        source=FILE_SOURCE_SUBMISSION,
        content_type=record.content_type,
        modified_at=aware(submission.submitted_at),
        revision=submission.revision,
    )
