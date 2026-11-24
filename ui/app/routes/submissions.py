"""Submission records: what ``/submit`` tells BERIL, and the feed built on it.

``POST /api/context/submissions`` is posted by the archive step after the
lakehouse upload succeeds, with the manifest of every archived file and a
bundle of the wiki's text files; ``PUT .../files/{path}`` adds each figure the
report embeds, one request per file; ``GET /api/context/submissions`` is the
"changed since" feed of complete submissions. The ingest tables are not
involved: the context-store mirror is best-effort and may never run.
"""

from __future__ import annotations

import io
import json
import logging
import zipfile
import zlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import BerilUser, require_user_api
from app.config import get_settings
from app.context_manager.base import (
    READABLE_FIGURES_DIR,
    ArchiveUnavailableError,
    is_readable_path,
)
from app.context_manager.openviking import context_slugify
from app.db.models import Submission, SubmissionFile
from app.db.session import get_db
from app.routes.data import _safe_relative_path
from app.routes.ingest_gate import archive_entry_count, check_approval_of, parse_beril_yaml, read_capped
from app.submissions.service import (
    KIND_APPROVED,
    SUBMISSION_COMPLETE,
    SUBMISSION_KINDS,
    SubmissionManifest,
    aware,
    complete_submissions_after,
    complete_submissions_since,
    content_type_for,
    find_submission,
    get_submission,
    missing_paths,
    refresh_status,
    report_text,
    sha256_hex,
    store_file,
)
from app.submissions.store import SubmissionStore, get_submission_store

logger = logging.getLogger(__name__)

ROUTER_SUBMISSIONS = APIRouter(tags=["context"])

MAX_SUBMISSIONS_LIMIT = 1000
STORE_UNAVAILABLE_DETAIL = "The submission store is currently unavailable."

_ALLOWED_COMPRESSION = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})


def _reject(detail: str, code: int = status.HTTP_422_UNPROCESSABLE_CONTENT) -> HTTPException:
    return HTTPException(status_code=code, detail=detail)


# Bundled for the approval check and kept with the record, but never served
# (not a readable path): the review the approval's review_hash names.
APPROVAL_ONLY_FILES = frozenset({"REVIEW.md"})


def _read_bundle(data: bytes) -> dict[str, bytes]:
    """The bundle's members as ``{path: bytes}``.

    Only wiki-readable text files may be bundled (figures go by PUT), so a
    bundle is small; it is still bounded the way an ingest archive is — entry
    count from the end record before the directory is parsed, each member
    and the total from the directory before anything is inflated.
    """
    settings = get_settings()
    count = archive_entry_count(data, stop_after=settings.context_max_archive_entries)
    if count is None:
        raise _reject("The bundle could not be read as a zip file.", status.HTTP_400_BAD_REQUEST)
    if count > settings.context_max_archive_entries:
        raise _reject("The bundle has too many entries.", status.HTTP_413_CONTENT_TOO_LARGE)
    members: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            infos = [i for i in zf.infolist() if not i.is_dir()]
            total = 0
            for info in infos:
                path = _safe_relative_path(info.filename)
                if path is None or path != info.filename.lstrip("./"):
                    raise _reject(f"Bundle entry has an unsafe name: {info.filename!r}", status.HTTP_400_BAD_REQUEST)
                if path not in APPROVAL_ONLY_FILES and (
                    path.startswith(READABLE_FIGURES_DIR) or not is_readable_path(path)
                ):
                    raise _reject(
                        f"Only the wiki's text files and REVIEW.md may be bundled; {path!r} "
                        "is not one (figures are sent one per PUT)."
                    )
                if info.compress_type not in _ALLOWED_COMPRESSION or info.flag_bits & 0x1:
                    raise _reject(f"{path} is encrypted or uses an unsupported compression.", status.HTTP_400_BAD_REQUEST)
                if info.file_size > settings.context_max_file_bytes:
                    raise _reject(f"{path} is too large.", status.HTTP_413_CONTENT_TOO_LARGE)
                total += info.file_size
            if total > settings.context_max_expanded_bytes:
                raise _reject("The bundle expands to too many bytes.", status.HTTP_413_CONTENT_TOO_LARGE)
            for info in infos:
                members[_safe_relative_path(info.filename)] = zf.read(info)
    except (zipfile.BadZipFile, OSError, zlib.error) as exc:
        raise _reject("The bundle could not be read as a zip file.", status.HTTP_400_BAD_REQUEST) from exc
    return members


def _parse_manifest(data: bytes) -> SubmissionManifest:
    try:
        return SubmissionManifest.model_validate(json.loads(data.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _reject("manifest.json is not valid JSON.", status.HTTP_400_BAD_REQUEST) from exc
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(p) for p in first.get("loc", ()))
        raise _reject(f"manifest.json: {where}: {first.get('msg')}") from exc


def _submission_payload(submission: Submission, *, missing: list[str]) -> dict:
    return {
        "id": submission.id,
        "project": submission.project,
        "owner_orcid": submission.owner_orcid,
        "address": f"{submission.owner_orcid}/{submission.project}",
        "revision": submission.revision,
        "submitted_at": aware(submission.submitted_at).isoformat(),
        "kind": submission.kind,
        "status": submission.status,
        "archive_path": submission.archive_path,
        "approval_by": submission.approval_by,
        "approval_at": aware(submission.approval_at).isoformat() if submission.approval_at else None,
        "files": [
            {"path": f.path, "sha256": f.sha256, "size": f.size, "stored": f.stored}
            for f in submission.files
        ],
        "missing": missing,
    }


def _feed_entry(submission: Submission) -> dict:
    return {
        "id": submission.id,
        "project": submission.project,
        "owner_orcid": submission.owner_orcid,
        "address": f"{submission.owner_orcid}/{submission.project}",
        "revision": submission.revision,
        "submitted_at": aware(submission.submitted_at).isoformat(),
        "kind": submission.kind,
        "archive_path": submission.archive_path,
        "approval_by": submission.approval_by,
        "approval_at": aware(submission.approval_at).isoformat() if submission.approval_at else None,
        # What a reader can fetch: REVIEW.md is stored for the approval but
        # not served, so it is not listed.
        "files": [
            {"path": f.path, "sha256": f.sha256, "size": f.size}
            for f in submission.files
            if f.stored and is_readable_path(f.path)
        ],
    }


async def _store_or_502(coro):
    try:
        return await coro
    except ArchiveUnavailableError as exc:
        logger.warning("Submission store unavailable: %s", exc)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=STORE_UNAVAILABLE_DETAIL) from exc


async def record_submission(
    db: AsyncSession,
    store: SubmissionStore,
    *,
    manifest: SubmissionManifest,
    bundle: dict[str, bytes],
    owner: BerilUser | None,
    kind: str,
    require_report: bool = True,
    reject_changed_manifest: bool = True,
) -> tuple[Submission, bool]:
    """Create the record (or find the existing one for this revision), store
    the bundled files, and settle its status. Returns ``(submission,
    created)``. Shared by ``/submit``'s post and the admin import.

    Every bundled file is checked against the manifest first — a file the
    manifest does not list, or whose bytes do not hash to the manifest's
    sha256, refuses the whole post before anything is written. A re-post of
    a recorded revision must carry the recorded manifest (409 otherwise)
    unless ``reject_changed_manifest`` is off, in which case the recorded
    files win; either way no byte is stored that the record does not name.
    """
    listed = {f.path: f for f in manifest.files}
    for path, data in bundle.items():
        entry = listed.get(path)
        if entry is None:
            raise _reject(f"{path} is bundled but not in the manifest.")
        if sha256_hex(data) != entry.sha256 or len(data) != entry.size:
            raise _reject(f"{path} does not match the manifest's sha256/size.")
    report = bundle.get("REPORT.md")
    if require_report and report is None:
        raise _reject("The bundle must carry REPORT.md.")
    if report is not None:
        if sha256_hex(report) != manifest.revision:
            raise _reject("revision is not the sha256 of the bundled REPORT.md.")
        if manifest.approval.report_hash and manifest.approval.report_hash != manifest.revision:
            raise _reject("approval.report_hash does not match REPORT.md.")

    existing = await find_submission(
        db, owner_orcid=manifest.owner_orcid, project=manifest.project, revision=manifest.revision
    )
    created = existing is None
    if existing is None:
        submission = Submission(
            owner_user_id=owner.id if owner is not None else None,
            owner_orcid=manifest.owner_orcid,
            project=manifest.project,
            revision=manifest.revision,
            submitted_at=manifest.submitted_at,
            archive_path=manifest.archive_path,
            approval_by=manifest.approval.by,
            approval_at=manifest.approval.at,
            kind=kind,
            files=[
                SubmissionFile(
                    path=f.path, sha256=f.sha256, size=f.size, content_type=content_type_for(f.path)
                )
                for f in manifest.files
            ],
        )
        db.add(submission)
        try:
            await db.flush()
        except IntegrityError:
            # A concurrent post of the same revision won; take theirs.
            await db.rollback()
            existing = await find_submission(
                db, owner_orcid=manifest.owner_orcid, project=manifest.project, revision=manifest.revision
            )
            created = False
    if not created:
        # Lock the recorded row and re-read it, as a figure PUT does, so the
        # two cannot settle status from each other's stale view.
        submission = await get_submission(db, existing.id, for_update=True)

    records = {f.path: f for f in submission.files}
    if not created and reject_changed_manifest:
        # The revision names REPORT.md only, so a re-post can carry other
        # files that changed since the first. Storing those would serve bytes
        # whose hash the feed does not advertise; refuse the whole re-post.
        persisted = {p: (r.sha256, r.size) for p, r in records.items()}
        incoming = {f.path: (f.sha256, f.size) for f in manifest.files}
        if incoming != persisted:
            changed = sorted(p for p in persisted.keys() | incoming.keys() if persisted.get(p) != incoming.get(p))
            raise _reject(
                f"This revision was already recorded with a different manifest ({', '.join(changed)}). "
                "Change REPORT.md to submit new files.",
                status.HTTP_409_CONFLICT,
            )
    for path, data in bundle.items():
        record = records.get(path)
        if record is not None and not record.stored:
            if sha256_hex(data) != record.sha256 or len(data) != record.size:
                raise _reject(f"{path} does not match the recorded sha256/size.", status.HTTP_409_CONFLICT)
            await _store_or_502(store_file(store, submission, record, data))
    await _store_or_502(refresh_status(db, store, submission))
    await db.commit()
    await db.refresh(submission, ["files"])
    return submission, created


def _check_bundled_approval(manifest_model, members: dict[str, bytes], *, caller_orcid: str) -> None:
    """The ingest gate's approval rule, on the bundled ``beril.yaml``, against
    the bundled ``REPORT.md`` and ``REVIEW.md`` bytes — never a hash the
    caller only lists, which nothing would check."""
    if "beril.yaml" not in members:
        raise _reject("The bundle must carry beril.yaml; the record rests on its approval.")

    def actual_sha256(name: str) -> str | None:
        return sha256_hex(members[name]) if name in members else None

    check_approval_of(
        parse_beril_yaml(members["beril.yaml"]),
        caller_orcid=caller_orcid,
        project_slug=manifest_model.project,
        slugify=context_slugify,
        actual_sha256=actual_sha256,
    )


@ROUTER_SUBMISSIONS.post("/api/context/submissions")
async def post_submission(
    request: Request,
    manifest: UploadFile = File(..., description="manifest.json: every archived file."),
    bundle: UploadFile = File(..., description="bundle.zip: the wiki's text files."),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Record one ``/submit`` with BERIL.

    ``manifest.json`` is ``{project, owner_orcid, revision, submitted_at,
    archive_path, approval: {by, at, report_hash}, files: [{path, sha256,
    size}]}`` and covers every archived file, figures included; ``bundle.zip``
    carries the wiki-readable text files (``REPORT.md``, ``README.md``,
    ``beril.yaml``, ``CORRECTIONS.md``, ``REFUTATION_<n>.md``) and
    ``REVIEW.md``. Each bundled
    file must hash to its manifest entry, ``revision`` and
    ``approval.report_hash`` must be the sha256 of ``REPORT.md``, and
    ``approval.by`` and ``owner_orcid`` must be the caller. The bundled
    ``beril.yaml`` must pass the ingest gate's approval rule: this project,
    ``status: complete``, approved by the caller, its ``report_hash`` and
    ``review_hash`` matching the bundled ``REPORT.md`` and ``REVIEW.md``.
    ``REVIEW.md`` is kept with the record but never served. Like the gate, this ties
    the record to a named approver who is the caller; it is not proof of
    review.

    Idempotent on ``(owner, project, revision)``: posting the same revision
    again returns the existing record (``created: false``) and stores any
    bundled file it still lacked. The response's ``missing`` lists the
    figures the report embeds that have yet to be PUT; the submission is
    ``complete`` once it is empty.
    """
    settings = get_settings()
    manifest_model = _parse_manifest(
        await read_capped(manifest, settings.context_max_manifest_bytes, what="manifest")
    )
    if manifest_model.owner_orcid != user.orcid_id:
        raise _reject("owner_orcid must be the caller.", status.HTTP_403_FORBIDDEN)
    if manifest_model.approval.by != user.orcid_id:
        raise _reject(
            "The project was approved by someone else; only its approver can record it.",
            status.HTTP_403_FORBIDDEN,
        )
    if context_slugify(manifest_model.project) != manifest_model.project:
        raise _reject(f"project must be a slug ({context_slugify(manifest_model.project)!r}).")
    for entry in manifest_model.files:
        if _safe_relative_path(entry.path) != entry.path:
            raise _reject(f"manifest path is not a clean relative path: {entry.path!r}")
    members = _read_bundle(
        await read_capped(bundle, settings.context_max_archive_bytes, what="bundle")
    )
    _check_bundled_approval(manifest_model, members, caller_orcid=user.orcid_id)
    submission, created = await record_submission(
        db, get_submission_store(), manifest=manifest_model, bundle=members, owner=user,
        kind=KIND_APPROVED,
    )
    logger.info(
        "Submission %s of %s/%s@%s recorded (%s, %s)",
        submission.id, submission.owner_orcid, submission.project, submission.revision[:12],
        "created" if created else "existing", submission.status,
    )
    report = await _store_or_502(report_text(get_submission_store(), submission))
    return {**_submission_payload(submission, missing=missing_paths(submission, report)), "created": created}


@ROUTER_SUBMISSIONS.get("/api/context/submissions/{submission_id}")
async def get_submission_status(
    submission_id: str,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """One submission with each file's stored flag and what is still missing."""
    submission = await get_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown submission.")
    report = await _store_or_502(report_text(get_submission_store(), submission))
    return _submission_payload(submission, missing=missing_paths(submission, report))


@ROUTER_SUBMISSIONS.put("/api/context/submissions/{submission_id}/files/{path:path}")
async def put_submission_file(
    submission_id: str,
    path: str,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Store one manifest file's bytes — the way figures arrive, one per
    request (the body is the file). Owner only; the bytes must hash to the
    manifest's sha256. Storing a file already stored stores nothing again.
    """
    submission = await get_submission(db, submission_id)
    # 404 rather than 403 for someone else's: a probe cannot confirm an id.
    if submission is None or submission.owner_orcid != user.orcid_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown submission.")
    clean = _safe_relative_path(path)
    record = next((f for f in submission.files if f.path == clean), None) if clean else None
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="That path is not in the manifest.")
    if not is_readable_path(record.path):
        raise _reject("Only the wiki's files are stored by BERIL.", status.HTTP_403_FORBIDDEN)
    limit = get_settings().submissions_max_file_bytes
    if record.size > limit:
        raise _reject(f"{record.path} exceeds the per-file limit ({limit} bytes).", status.HTTP_413_CONTENT_TOO_LARGE)
    data = await request.body()
    if len(data) > limit:
        raise _reject("The file is too large.", status.HTTP_413_CONTENT_TOO_LARGE)
    if not record.stored and (sha256_hex(data) != record.sha256 or len(data) != record.size):
        raise _reject(f"{record.path} does not match the manifest's sha256/size.")
    # Concurrent PUTs of a submission's last figures must not each settle
    # status from a stale view of the others; lock the row, re-read the
    # files, then store and recompute. Status is recomputed whenever the
    # submission is still pending, so retrying a stored file also repairs it.
    store = get_submission_store()
    submission = await get_submission(db, submission_id, for_update=True)
    if submission is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown submission.")
    record = next(f for f in submission.files if f.path == record.path)
    if not record.stored:
        await _store_or_502(store_file(store, submission, record, data))
    if submission.status != SUBMISSION_COMPLETE:
        await _store_or_502(refresh_status(db, store, submission))
    await db.commit()
    return {
        "id": submission.id,
        "path": record.path,
        "stored": True,
        "status": submission.status,
        "missing": missing_paths(
            submission, await _store_or_502(report_text(get_submission_store(), submission))
        ),
    }


def _parse_since(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise _reject("`since` must be an ISO 8601 date or datetime.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_kinds(value: str) -> tuple[str, ...]:
    kinds = tuple(dict.fromkeys(k.strip() for k in value.split(",") if k.strip()))
    if not kinds or any(k not in SUBMISSION_KINDS for k in kinds):
        raise _reject("`kind` must name one or more of: " + ", ".join(SUBMISSION_KINDS) + ".")
    return kinds


@ROUTER_SUBMISSIONS.get("/api/context/submissions")
async def list_submissions(
    request: Request,
    after: int | None = Query(default=None, ge=0, description="Feed position; only submissions after it (exclusive). Pass back the previous page's `next_after`; omit to start from the beginning."),
    since: str | None = Query(default=None, description="Deprecated: ISO 8601 instant, paging by `submitted_at`. Can miss a submission that completes after a later one; use `after`."),
    kind: str = Query(default="approved,seeded", description="Comma-separated: approved, seeded, docs."),
    limit: int = Query(default=100, ge=1, le=MAX_SUBMISSIONS_LIMIT),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """What was submitted, and when — the "changed since" feed.

    One entry per **complete** submission, in the order they completed: its
    id, project, owner, address, ``revision`` (sha256 of REPORT.md),
    ``submitted_at``, ``kind`` (``approved`` for a ``/submit``, ``seeded``
    for an admin import of a project that predates it, ``docs`` for the
    central digests), the archive path, and each stored file with its sha256
    and size — the bytes ``/read`` serves byte-exact. Every submission is of
    an approved project, so the feed is global like every read.

    ``next_after`` is the cursor for the page after this one; an empty page
    echoes the caller's own. A submission can complete after a later one
    (its figures arrived last), so the feed is not ordered by
    ``submitted_at``, and a project's entries can arrive out of revision
    order: keep the one with the newest ``submitted_at``.

    ``since``/``next_since`` is the old cursor, kept for clients not yet on
    ``after``; it pages by ``submitted_at`` and can skip submissions.
    """
    kinds = _parse_kinds(kind)
    if since is not None:
        if after is not None:
            raise _reject("Pass `after` or `since`, not both.")
        since_at = _parse_since(since)
        rows = await complete_submissions_since(db, since=since_at, kinds=kinds, limit=limit)
        return {
            "submissions": [_feed_entry(s) for s in rows],
            "next_since": aware(rows[-1].submitted_at).isoformat() if rows else since,
        }
    rows = await complete_submissions_after(db, after=after, kinds=kinds, limit=limit)
    return {
        "submissions": [_feed_entry(s) for s in rows],
        "next_after": rows[-1].feed_seq if rows else after,
    }
