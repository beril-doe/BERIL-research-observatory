"""Routes abstracting an LLM context manager

This puts any context manager queries - i.e. to OpenViking - behind a common API so
the user / consumer doesn't need to know any details.

This provides a mechanism to query the context manager RAG db with a reasonably
simple API. It also provides API calls for the user / agent to manage their data
within BERIL's context manager implementation.
"""

import logging
from collections import Counter

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
    INGEST_STATUSES,
    INGEST_UNKNOWN,
    TERMINAL_INGEST_STATUSES,
    IngestBatchStatus,
    IngestFileStatus,
)
from app.context_manager.openviking import (
    ContextIngestFile,
    ContextQuery,
    OpenVikingManager,
    OvProvisioningError,
    UnauthenticatedError,
    context_slugify,
    get_user_ov_api_key,
    user_target_root,
)
from app.db.crud import (
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
):
    logger.info(f"Running context query: {query} for user {user.orcid_id}")
    manager = await resolve_context_manager(db, user)
    return await manager.query(query)

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


@ROUTER_CONTEXT.post("/api/context/ingest_file")
async def post_context_ingest_file(
    request: Request,
    project: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    """Ingest one or more files into the user's context manager.

    Files are queued for indexing, not indexed synchronously — a ``queued``
    status means the context manager accepted the file, and it becomes
    searchable some time later. Each file reports its own status, so a partial
    batch still returns 200 with the failures named.
    """
    settings = get_settings()
    manager = await resolve_context_manager(db, user)
    db_project = await _resolve_project(db, user, project)

    supplied = [f for f in files if f.filename]
    if len(supplied) > settings.context_max_ingest_files:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                f"Too many files: {len(supplied)} "
                f"(limit {settings.context_max_ingest_files})."
            ),
        )

    # Validate every name before reading anything, so a bad filename anywhere
    # in the batch queues nothing.
    relative_paths = []
    for f in supplied:
        relative_path = _safe_relative_path(f.filename or "")
        if relative_path is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid filename: {f.filename!r}",
            )
        relative_paths.append(relative_path)

    ingest_files = []
    for f, relative_path in zip(supplied, relative_paths):
        content = await f.read()
        if len(content) > settings.context_max_file_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=(
                    f"{relative_path} is too large: {len(content)} bytes "
                    f"(limit {settings.context_max_file_bytes})."
                ),
            )
        ingest_files.append(
            ContextIngestFile(
                relative_path=relative_path,
                content=content,
                content_type=f.content_type,
            )
        )

    target_root = user_target_root(user.orcid_id, db_project.slug)
    logger.info(
        "Ingesting %d file(s) to %s for user %s",
        len(ingest_files),
        target_root,
        user.orcid_id,
    )
    results = await manager.insert_files(ingest_files, target_root=target_root)

    # Record the submission so its progress stays pollable: the context
    # manager expires its own task records and does not track who owns them.
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
            }
            for r in results.results
        ],
    )
    results.batch_id = batch.id
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
    """
    statuses = {f.status for f in files}
    if INGEST_FAILED in statuses:
        return INGEST_FAILED
    if statuses & {INGEST_QUEUED, INGEST_PROCESSING}:
        return INGEST_PROCESSING
    if INGEST_UNKNOWN in statuses:
        return INGEST_UNKNOWN
    return INGEST_COMPLETED
