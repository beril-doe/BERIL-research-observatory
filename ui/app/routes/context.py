"""Routes abstracting an LLM context manager

This puts any context manager queries - i.e. to OpenViking - behind a common API so
the user / consumer doesn't need to know any details.

This provides a mechanism to query the context manager RAG db with a reasonably
simple API. It also provides API calls for the user / agent to manage their data
within BERIL's context manager implementation.
"""

import asyncio
import hashlib
import io
import logging
import mimetypes
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import BerilUser, require_user_api
from app.config import get_settings
from app.context_manager.base import (
    INGEST_COMPLETED,
    INGEST_FAILED,
    INGEST_PROCESSING,
    INGEST_QUEUED,
    INGEST_SKIPPED,
    INGEST_STATUSES,
    INGEST_UNKNOWN,
    TERMINAL_INGEST_STATUSES,
    ContextIngestResults,
    ContextQueryResults,
    IngestBatchStatus,
    IngestFileStatus,
    IngestResult,
)
from app.context_manager.openviking import (
    QUERY_FAILURES,
    ContextIngestFile,
    ContextQuery,
    OpenVikingManager,
    OvProvisioningError,
    UnauthenticatedError,
    context_slugify,
    get_user_ov_api_key,
    target_uri,
    user_target_root,
)
from app.db.crud import (
    completed_file_hashes,
    create_ingest_batch,
    create_user_project,
    get_ingest_batch,
    get_project_by_slug,
    update_ingest_file_statuses,
)
from app.db.models import UserProject
from app.db.session import get_db
from app.routes.data import _safe_relative_path

logger = logging.getLogger()

def get_context_manager(api_key: str) -> OpenVikingManager:
    return OpenVikingManager(get_settings(), api_key)


async def resolve_context_manager(
    db: AsyncSession, user: BerilUser
) -> OpenVikingManager:
    """Build a context manager for ``user``, provisioning their backing
    credential on first use.

    The backing store is an implementation detail, so its failures surface as
    a generic 502 rather than anything the user is expected to act on.
    """
    try:
        api_key = await get_user_ov_api_key(db, user)
    except UnauthenticatedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
    except OvProvisioningError as exc:
        logger.warning("Context manager unavailable for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager is currently unavailable.",
        ) from exc
    return get_context_manager(api_key)


ROUTER_CONTEXT = APIRouter(tags=["context"])

@ROUTER_CONTEXT.post("/api/context/find")
async def post_context_find(
    query: ContextQuery,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
) -> ContextQueryResults:
    """Semantic search over the caller's context layer.

    Bounds and types are enforced by ``ContextQuery``, so a malformed request
    is a 422 before the backend is touched. A backend that rejects or cannot
    answer the query surfaces as 502 — the store is an implementation detail,
    so its error text is logged rather than returned.
    """
    logger.info(
        "Context query %r (limit=%d) for user %s",
        query.query,
        query.limit,
        user.orcid_id,
    )
    manager = await resolve_context_manager(db, user)
    try:
        return await manager.query(query)
    except QUERY_FAILURES as exc:
        logger.warning("Context query failed for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager could not answer that query.",
        ) from exc

@ROUTER_CONTEXT.get("/api/context/ls")
async def get_context_files(
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    manager = await resolve_context_manager(db, user)
    return await manager.list_files()

async def _resolve_project(
    db: AsyncSession, user: BerilUser, project: str
) -> UserProject:
    """Find the caller's project by slug, creating it if it doesn't exist.

    Ownership is not enforced: an existing project of the same slug is reused
    whoever owns it, because the ingest target is keyed on the *uploader's*
    ORCiD and so cannot reach another user's namespace. Revisit when ingest
    starts writing ProjectFile rows.
    """
    slug = context_slugify(project)
    if not slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid project name: {project!r}",
        )

    existing = await get_project_by_slug(db, user.id, slug)
    if existing is not None:
        return existing
    try:
        return await create_user_project(db, user.id, title=project, slug=slug)
    except IntegrityError:
        # A concurrent request created it first; take theirs.
        await db.rollback()
        existing = await get_project_by_slug(db, user.id, slug)
        if existing is None:
            raise
        return existing


def _extract_archive(archive_bytes: bytes, dest: Path) -> None:
    """Unpack a zip archive into ``dest``, rejecting anything that escapes it.

    ``zipfile`` sanitizes ordinary traversal in member names, but it happily
    restores symlinks, which would let a later member be written outside
    ``dest`` through the link. Members are therefore checked before any of them
    is written — a hostile archive extracts nothing.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
            for info in zf.infolist():
                # Upper 16 bits of external_attr are the Unix mode; 0xA000 is
                # S_IFLNK. Directories and regular files are the only members
                # we restore.
                if (info.external_attr >> 16) & 0xF000 == 0xA000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Archive contains a symlink: {info.filename!r}",
                    )
                resolved = (dest / info.filename).resolve()
                if not resolved.is_relative_to(dest):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Archive entry escapes the archive root: {info.filename!r}",
                    )
            zf.extractall(dest)
    except (zipfile.BadZipFile, OSError) as exc:
        logger.warning("Rejected ingest archive: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded archive could not be read as a zip file.",
        ) from exc


def _parse_manifest(manifest_bytes: bytes) -> list[str]:
    """Read the manifest into a list of sanitized relative paths.

    One path per line; blank lines are ignored so a trailing newline is fine.
    Paths are sanitized the same way upload filenames are, and duplicates are
    dropped so a repeated line does not ingest the same file twice.
    """
    try:
        text = manifest_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The manifest must be UTF-8 text.",
        ) from exc

    paths: list[str] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        relative_path = _safe_relative_path(line)
        if relative_path is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid manifest path on line {line_no}: {line!r}",
            )
        if relative_path not in seen:
            seen.add(relative_path)
            paths.append(relative_path)

    if not paths:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The manifest lists no files.",
        )
    return paths


@ROUTER_CONTEXT.post("/api/context/ingest_files")
async def post_context_ingest_files(
    request: Request,
    project: str = Form(...),
    archive: UploadFile = File(...),
    manifest: UploadFile = File(...),
    force: bool = Form(False),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    """Ingest the manifest-listed files of a zip archive into the context manager.

    The archive carries the caller's directory structure, which a plain
    multipart upload loses; the manifest names which of its members to ingest,
    one relative path per line, so an archive may carry more than it ingests.
    Each path is kept relative to the project's ingest root.

    Files are queued for indexing, not indexed synchronously — a ``queued``
    status means the context manager accepted the file, and it becomes
    searchable some time later. Each file reports its own status, so a partial
    batch still returns 200 with the failures named.

    A file whose content already *completed* an ingest for this project is
    skipped rather than re-sent, making a re-submission of unchanged work a
    no-op. Only ``completed`` counts: a file that failed, is still in flight, or
    predates content hashing re-ingests, so a user's retry after a failure
    always does something. ``force=true`` bypasses the check entirely — the
    repair path for content the backend lost or must re-index.

    When every file is skipped nothing is submitted, so no batch exists and
    ``batch_id`` is ``None``. That is success, not a missing handle.
    """
    settings = get_settings()
    manager = await resolve_context_manager(db, user)
    db_project = await _resolve_project(db, user, project)
    target_root = user_target_root(user.orcid_id, db_project.slug)

    archive_bytes = await archive.read()

    relative_paths = _parse_manifest(await manifest.read())
    if len(relative_paths) > settings.context_max_ingest_files:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                f"Too many files: {len(relative_paths)} "
                f"(limit {settings.context_max_ingest_files})."
            ),
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir).resolve()
        # Unpacking touches the disk, so it stays off the event loop.
        await asyncio.to_thread(_extract_archive, archive_bytes, root)

        # Check the whole manifest against the archive before reading anything,
        # so a manifest naming a missing file queues nothing.
        missing = [p for p in relative_paths if not (root / p).is_file()]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Manifest files missing from the archive: {', '.join(missing)}",
            )

        logger.info(f"ingesting files: {relative_paths}")

        # What this project already has, so identical content is not re-sent.
        # Skipped entirely under force: the point of the flag is to re-ingest
        # regardless of what we believe already landed.
        landed = {} if force else await completed_file_hashes(db, db_project.id)

        ingest_files = []
        content_hashes: dict[str, str] = {}
        skipped: list[IngestResult] = []
        for relative_path in relative_paths:
            source = root / relative_path
            size = source.stat().st_size
            if size > settings.context_max_file_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=(
                        f"{relative_path} is too large: {size} bytes "
                        f"(limit {settings.context_max_file_bytes})."
                    ),
                )
            content = await asyncio.to_thread(source.read_bytes)
            # Recorded against the batch row so a later ingest can tell whether
            # this exact content already landed.
            digest = hashlib.sha256(content).hexdigest()
            if landed.get(relative_path) == digest:
                # Reported, not omitted: the response accounts for every
                # manifest entry so a skip can't be mistaken for a lost file.
                # No batch row is written — a skip is not an ingest attempt, and
                # recording one would let it satisfy a later skip check without
                # anything ever having been indexed.
                skipped.append(
                    IngestResult(
                        relative_path=relative_path,
                        status=INGEST_SKIPPED,
                        uri=target_uri(target_root, relative_path),
                        reason="Identical content already ingested.",
                    )
                )
                continue
            content_hashes[relative_path] = digest
            ingest_files.append(
                ContextIngestFile(
                    relative_path=relative_path,
                    content=content,
                    content_type=mimetypes.guess_type(relative_path)[0],
                )
            )

    logger.info(
        "Ingesting %d file(s) to %s for user %s (%d unchanged)",
        len(ingest_files),
        target_root,
        user.orcid_id,
        len(skipped),
    )

    # Everything was unchanged: nothing to submit, so no batch and nothing to
    # poll. Answered as a success with the skips enumerated.
    if not ingest_files:
        return ContextIngestResults(
            results=skipped, queued=0, failed=0, skipped=len(skipped)
        )

    results = await manager.insert_files(ingest_files, target_root=target_root)

    # Record the submission so its progress stays pollable: the context
    # manager expires its own task records and does not track who owns them.
    # Only submitted files get rows — see the skip branch above.
    batch = await create_ingest_batch(
        db,
        user_id=user.id,
        project_id=db_project.id,
        target_root=target_root,
        files=[
            {
                "relative_path": r.relative_path,
                "uri": r.uri,
                "ov_task_id": r.task_id,
                "status": r.status,
                "error": r.reason,
                "content_sha256": content_hashes.get(r.relative_path),
            }
            for r in results.results
        ],
    )
    results.batch_id = batch.id
    results.results = results.results + skipped
    results.skipped = len(skipped)
    return results


@ROUTER_CONTEXT.get("/api/context/ingest_status/{batch_id}")
async def get_context_ingest_status(
    request: Request,
    batch_id: str,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
) -> IngestBatchStatus:
    """Report the progress of a previous ingest submission.

    Files that already reached a terminal state are never re-polled, so a
    result stays readable long after the context manager has forgotten the
    underlying task.
    """
    batch = await get_ingest_batch(db, batch_id)
    # 404 rather than 403 on a foreign batch: a probe should not be able to
    # confirm that someone else's batch id exists.
    if batch is None or batch.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown ingest batch."
        )

    pending = {
        f.ov_task_id: f.id
        for f in batch.files
        if f.status not in TERMINAL_INGEST_STATUSES and f.ov_task_id
    }
    if pending:
        manager = await resolve_context_manager(db, user)
        refreshed = await manager.task_statuses(list(pending))
        # An unreachable backend reports "unknown" for everything; keep what we
        # already know rather than overwriting it with that.
        updates = {
            pending[task_id]: value
            for task_id, value in refreshed.items()
            if value[0] != INGEST_UNKNOWN
        }
        await update_ingest_file_statuses(db, updates)
        for f in batch.files:
            if f.id in updates:
                f.status, f.error = updates[f.id]

    files = [
        IngestFileStatus(
            relative_path=f.relative_path, status=f.status, uri=f.uri, error=f.error
        )
        for f in batch.files
    ]
    counts = Counter(f.status for f in files)
    return IngestBatchStatus(
        batch_id=batch.id,
        project=batch.project.slug,
        status=_rollup_status(files),
        counts={s: counts.get(s, 0) for s in INGEST_STATUSES},
        files=files,
    )


def _rollup_status(files: list[IngestFileStatus]) -> str:
    """Collapse per-file statuses into one batch verdict.

    Failure wins over everything — a batch with a failed file is not a success,
    however many others landed. Unfinished work outranks a clean sweep, and
    ``unknown`` only surfaces once nothing is still in flight.

    ``skipped`` never appears here: a skipped file is not submitted and so
    writes no batch row. It is reported only in the ingest response.
    """
    statuses = {f.status for f in files}
    if INGEST_FAILED in statuses:
        return INGEST_FAILED
    if statuses & {INGEST_QUEUED, INGEST_PROCESSING}:
        return INGEST_PROCESSING
    if INGEST_UNKNOWN in statuses:
        return INGEST_UNKNOWN
    return INGEST_COMPLETED
