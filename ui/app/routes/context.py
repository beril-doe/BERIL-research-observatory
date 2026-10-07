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
from dataclasses import dataclass
from glob import escape as glob_escape
from pathlib import Path
from typing import NamedTuple

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
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
    INGEST_EXPIRED,
    INGEST_FAILED,
    INGEST_NOT_FOUND,
    INGEST_PROCESSING,
    INGEST_QUEUED,
    INGEST_REMOVED,
    INGEST_SKIPPED,
    INGEST_STATUSES,
    INGEST_UNKNOWN,
    MAX_DISCOVERY_LIMIT,
    MAX_GREP_NODE_LIMIT,
    MAX_LS_NODE_LIMIT,
    MAX_OWNER_EXPANSION,
    MAX_PITFALL_LIMIT,
    TERMINAL_INGEST_STATUSES,
    ContextIngestResults,
    ContextQueryResults,
    DiscoveryHit,
    DiscoveryResults,
    IngestBatchStatus,
    IngestFileStatus,
    IngestResult,
    PitfallHit,
    PitfallResults,
)
from app.context_manager.openviking import (
    HOUSE_ACCOUNT_ID,
    QUERY_FAILURES,
    USERS_TARGET_URI,
    ContextIngestFile,
    ContextQuery,
    OpenVikingManager,
    OvProvisioningError,
    UnauthenticatedError,
    apply_discovery_precedence,
    context_slugify,
    corpus_root,
    get_user_ov_api_key,
    listing_uri,
    target_uri,
    user_target_root,
)
from app.db.crud import (
    completed_file_hashes,
    create_ingest_batch,
    create_user_project,
    get_ingest_batch,
    get_project_by_slug,
    latest_file_statuses,
    projects_with_memory,
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
    """Semantic search over ingested content.

    Addressed like ``/ls`` and ``/grep`` — global reads, ``owner``/
    ``all_owners`` to widen, a bare ``project`` meaning the caller's own — with
    one deliberate difference: a query with no addressing at all spans the
    whole corpus, where a bare listing shows the caller's own projects. A
    listing answers "what do I have"; a search answers "what does anyone
    know", and defaulting it to one namespace would hide the shared work the
    corpus exists for. The query never names a backend location directly:
    that would let it search outside the corpus, and the backend's own
    default scope is wider than the corpus too.

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
    unaddressed = query.project is None and query.owner is None
    target = _read_uri(
        user,
        query.project,
        query.path,
        owner=query.owner,
        all_owners=query.all_owners or unaddressed,
    )
    manager = await resolve_context_manager(db, user)
    try:
        return await manager.query(
            query, target_uri=await _expand_read_target(manager, target)
        )
    except QUERY_FAILURES as exc:
        logger.warning("Context query failed for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager could not answer that query.",
        ) from exc

@dataclass(frozen=True)
class _EveryOwner:
    """A read target naming one project under every owner.

    The owner segment is a wildcard, so this cannot be a URI until the backend
    says which owners have the project. ``_read_uri`` returns it unresolved
    because it deliberately runs before any backend is in hand — validation
    must not depend on provisioning — and ``_expand_read_target`` finishes it.
    ``pattern`` is relative to the corpus root and already traversal-checked.
    """

    pattern: str


async def _expand_read_target(
    manager: OpenVikingManager, target: "str | _EveryOwner"
) -> str | list[str]:
    """Turn a resolved read target into what the manager searches.

    A plain URI passes through. An every-owner target becomes the list of
    concrete URIs the backend knows — possibly empty, which the manager treats
    as "search nothing" rather than falling back to a wider scope.

    The expansion is capped at ``MAX_OWNER_EXPANSION`` and refused beyond it
    (422, asking for an ``owner``) rather than silently narrowed: the backend
    stops matching at its limit, so a read past the cap would quietly drop
    owners. One extra match is asked for, to tell "exactly the cap" from
    "more than the cap".
    """
    if isinstance(target, str):
        return target
    uris = await manager.glob(
        target.pattern, corpus_root(), node_limit=MAX_OWNER_EXPANSION + 1
    )
    if len(uris) > MAX_OWNER_EXPANSION:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"More than {MAX_OWNER_EXPANSION} owners have this project; "
                "name an `owner` to narrow the read."
            ),
        )
    return uris


def _read_uri(
    user: BerilUser,
    project: str | None,
    path: str | None,
    *,
    owner: str | None = None,
    all_owners: bool = False,
    path_field: str = "path",
    project_field: str = "project",
    owner_field: str = "owner",
) -> "str | _EveryOwner":
    """Resolve a **read** target. The single place caller input becomes an address.

    Reads are global — a submitted project is owned by one user and readable by
    everyone — so the owner narrows the target rather than authorizing it:

    * ``project`` alone → the **caller's own**. The safe default: a typo must
      not silently read someone else's work, and it matches how ``/submit``
      names projects.
    * ``owner`` → that owner's, whoever they are.
    * ``all_owners`` without a ``project`` → the whole corpus.
    * ``all_owners`` with a ``project`` → that project under **every owner
      who has one**, returned as an ``_EveryOwner`` for the route to expand.
      The owner segment is unknown here, and a project name alone is not an
      address — dropping it would silently widen the read to the corpus.

    Traversal is refused, with the corpus root as the boundary rather than any
    one owner. Writes must not be routed through here — they stay pinned to the
    authenticated ORCiD via ``user_target_root``.
    """
    if owner and all_owners:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"`{owner_field}` and `all_{owner_field}s` are mutually exclusive.",
        )
    if path and not project:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"`{path_field}` requires `{project_field}`.",
        )

    slug = None
    if project is not None:
        slug = context_slugify(project)
        if not slug:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid project name: {project!r}",
            )

    try:
        if all_owners and slug is None:
            return listing_uri()
        if all_owners:
            # The path is caller input and may itself hold glob characters;
            # escaped so it matches literally. The slug cannot: slugification
            # leaves only word characters and hyphens.
            segments = ["*", slug] + ([glob_escape(path)] if path else [])
            pattern = "/".join(segments)
            # Traversal-checked the same way a concrete URI is; the result is
            # discarded because the owner segment is still a wildcard.
            target_uri(corpus_root(), pattern)
            return _EveryOwner(pattern)
        return listing_uri(owner or user.orcid_id, slug, path)
    except ValueError as exc:
        logger.warning("Rejected read target for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid {path_field} or {owner_field}.",
        ) from exc


@ROUTER_CONTEXT.get("/api/context/ls")
async def get_context_files(
    request: Request,
    project: str | None = Query(
        default=None,
        description="Project to list. Omitted lists the owner's projects.",
    ),
    path: str | None = Query(
        default=None, description="Relative path within the project."
    ),
    owner: str | None = Query(
        default=None,
        description="Owner's ORCiD. Defaults to the caller.",
    ),
    all_owners: bool = Query(
        default=False, description="List across every owner's projects."
    ),
    recursive: bool = Query(default=False),
    simple: bool = Query(default=False, description="Return paths only."),
    node_limit: int | None = Query(default=None, ge=1, le=MAX_LS_NODE_LIMIT),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
) -> list:
    """List ingested content.

    Every submitted project is readable by everyone — owned by one user, like a
    public repository — so a listing is not restricted to the caller. ``owner``
    narrows to one person and ``all_owners`` spans the corpus; a bare
    ``project`` means the caller's own, which is the safe default for a name
    many owners may share.

    Addressed by project and path rather than by URI. A URI would let a caller
    name anything in the resource tree, including places outside the corpus;
    this way traversal is refused and the address is always well-formed.

    ``path`` without a ``project`` is rejected: it would otherwise resolve
    against a namespace root and list across projects.

    An un-ingested project lists empty rather than 404 — a legitimate state,
    and distinguishing it would report on what an owner has yet to write.
    """
    target = _read_uri(user, project, path, owner=owner, all_owners=all_owners)

    manager = await resolve_context_manager(db, user)
    try:
        return await manager.list_files(
            await _expand_read_target(manager, target),
            recursive=recursive,
            simple=simple,
            node_limit=node_limit,
        )
    except QUERY_FAILURES as exc:
        logger.warning("Context listing failed for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager could not list that path.",
        ) from exc


def _classify_pitfall(uri: str) -> tuple[str, str | None, str | None]:
    """Split a document URI into ``(origin, project, owner)``.

    Central docs live under the house account and belong to no project;
    everything else is a project's own ``memories/pitfalls.md``. Derived from
    the URI rather than asked of the backend, which does not model ownership.
    """
    rest = uri.removeprefix(USERS_TARGET_URI).strip("/")
    segments = rest.split("/")
    owner = segments[0] if segments else None
    if owner == HOUSE_ACCOUNT_ID:
        return "central", None, owner
    project = segments[1] if len(segments) > 1 else None
    return "project_memory", project, owner


@ROUTER_CONTEXT.get("/api/context/pitfalls")
async def get_context_pitfalls(
    request: Request,
    q: str | None = Query(
        default=None,
        description=(
            "Error text, table name, or description. Omit to list every "
            "pitfall document in scope."
        ),
    ),
    project: str | None = Query(
        default=None,
        description=(
            "Narrow the project memories to one project. The central archive "
            "is always included."
        ),
    ),
    owner: str | None = Query(
        default=None, description="Owner of `project`. Defaults to the caller."
    ),
    exact: bool = Query(
        default=False,
        description="Match tokens literally instead of semantically.",
    ),
    limit: int = Query(default=10, ge=1, le=MAX_PITFALL_LIMIT),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
) -> PitfallResults:
    """Has this gotcha been hit before, on any project?

    The question ``pitfall-capture`` asks by protocol, as one call. It spans
    both halves of the corpus — every project's ``memories/pitfalls.md`` and
    the central archive — so a caller does not have to know that pitfalls live
    in two shapes, nor compose a URI to reach them.

    ``exact`` matches tokens literally, which beats semantic search for error
    strings and table names — the things a user actually pastes in. Semantic is
    the default because a described symptom rarely shares wording with the
    entry that documents it.

    Results are documents, not fragments. The backend decomposes each file into
    section-level nodes, so a raw search returns several pieces of the same
    pitfall; these are grouped, with the document's best fragment score, and
    backend-generated stubs dropped. Only pitfall documents are ever searched
    or returned — never a project's REPORT, or another central doc.

    ``project`` / ``owner`` narrow the *project memories*, addressed like every
    other read (a bare ``project`` is the caller's own). The central archive
    stays in: it is shared knowledge relevant to any project, and its entries
    tagged with that project are that project's legacy pitfalls.

    Omitting ``q`` lists every pitfall document in scope, unranked, with
    ``total`` saying how many there are. An empty ``q`` is a malformed query
    and is rejected, not read as a listing.
    """
    _reject_empty_query(q, noun="pitfall")
    memory_pattern = _memory_pattern(user, project, owner, memory="pitfalls")

    manager = await resolve_context_manager(db, user)
    try:
        documents, scanned, total = await manager.find_pitfalls(
            q, memory_pattern=memory_pattern, limit=limit, exact=exact
        )
    except QUERY_FAILURES as exc:
        logger.warning("Pitfall query failed for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager could not answer that query.",
        ) from exc

    results = []
    for doc in documents:
        origin, doc_project, doc_owner = _classify_pitfall(doc["uri"])
        results.append(
            PitfallHit(
                uri=doc["uri"],
                origin=origin,
                project=doc_project,
                owner=doc_owner,
                score=doc["score"],
                excerpts=doc["excerpts"],
                fragment_uris=doc["fragment_uris"],
            )
        )
    return PitfallResults(
        query=q, results=results, fragments_scanned=scanned, total=total
    )


def _reject_empty_query(q: str | None, *, noun: str) -> None:
    """An omitted ``q`` is a listing; an empty one is a malformed query."""
    if q is not None and not q.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"`q` must not be empty; omit it to list every {noun}.",
        )


def _memory_pattern(
    user: BerilUser, project: str | None, owner: str | None, *, memory: str
) -> str:
    """The glob, relative to the corpus root, naming the memories in scope.

    ``memory`` is the memory's name (``pitfalls`` or ``discoveries``).
    Validated through ``_read_uri`` like every read address, so traversal in
    ``project`` or ``owner`` is refused the same way; the resolved location
    then gains the memory file's path. Unnamed segments are wildcards.
    """
    path = f"memories/{memory}.md"
    if not project and not owner:
        return f"*/*/{path}"
    resolved = _read_uri(user, project, None, owner=owner)
    relative = resolved.removeprefix(corpus_root()).strip("/")
    return f"{relative}/{path}" if project else f"{relative}/*/{path}"


@ROUTER_CONTEXT.get("/api/context/discoveries")
async def get_context_discoveries(
    request: Request,
    q: str | None = Query(
        default=None,
        description=(
            "Theme, organism, or pattern. Omit to list every discovery "
            "document in scope."
        ),
    ),
    project: str | None = Query(
        default=None,
        description=(
            "Narrow the project memories to one project. The central archive "
            "is always included."
        ),
    ),
    owner: str | None = Query(
        default=None, description="Owner of `project`. Defaults to the caller."
    ),
    exact: bool = Query(
        default=False, description="Match tokens literally instead of semantically."
    ),
    limit: int = Query(default=10, ge=1, le=MAX_DISCOVERY_LIMIT),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
) -> DiscoveryResults:
    """What has already been found, across every project?

    Spans both halves of the corpus like ``/pitfalls``, but applies the
    precedence rule that ``suggest-research`` Step 4 currently states as prose
    for an agent to re-implement per call site:

    * a project's own ``memories/discoveries.md`` wins;
    * a central entry tagged for a project that has one is a **stale
      duplicate** and is suppressed;
    * a central entry tagged for a project with no memory is legacy content and
      still counts;
    * an untagged central entry is background and always counts.

    Implemented once here so every caller gets the same combined view. The
    count of suppressed duplicates is reported rather than hidden, so a caller
    can tell "nothing matched" from "the current copy answered instead".

    Per-project memories are written at ``/submit`` approval, so this corpus is
    review-vetted by construction — a draft finding never reaches it.

    Scoped like ``/pitfalls``: only discovery documents are searched or
    returned, ``project``/``owner`` narrow the memories while the archive stays
    in, and omitting ``q`` lists every discovery document (an empty ``q`` is
    rejected). Precedence is applied before ``limit``.
    """
    _reject_empty_query(q, noun="discovery")
    memory_pattern = _memory_pattern(user, project, owner, memory="discoveries")

    manager = await resolve_context_manager(db, user)
    try:
        documents, scanned = await manager.find_discoveries(
            q, memory_pattern=memory_pattern, limit=limit, exact=exact
        )
    except QUERY_FAILURES as exc:
        logger.warning("Discovery query failed for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager could not answer that query.",
        ) from exc

    # Precedence before the limit: a stale central duplicate dropped after
    # trimming would have taken a page slot from the current copy.
    owned = await projects_with_memory(db, "discoveries")
    classified, suppressed = apply_discovery_precedence(
        documents, projects_with_memory=owned
    )
    total = len(classified)
    classified = classified[:limit]

    return DiscoveryResults(
        query=q,
        results=[
            DiscoveryHit(
                uri=doc["uri"],
                origin=doc["origin"],
                project=doc["project"],
                owner=doc["owner"],
                score=doc["score"],
                excerpts=doc["excerpts"],
                fragment_uris=doc["fragment_uris"],
            )
            for doc in classified
        ],
        fragments_scanned=scanned,
        suppressed=suppressed,
        total=total,
    )


@ROUTER_CONTEXT.get("/api/context/grep")
async def get_context_grep(
    request: Request,
    pattern: str = Query(min_length=1, description="Pattern to match."),
    project: str | None = Query(
        default=None,
        description="Project to search. Omitted searches the owner's projects.",
    ),
    path: str | None = Query(
        default=None, description="Relative path within the project."
    ),
    owner: str | None = Query(
        default=None, description="Owner's ORCiD. Defaults to the caller."
    ),
    all_owners: bool = Query(
        default=False, description="Search across every owner's projects."
    ),
    case_insensitive: bool = Query(default=False),
    exclude_project: str | None = Query(
        default=None, description="Project to exclude from the search."
    ),
    exclude_path: str | None = Query(
        default=None, description="Relative path within `exclude_project`."
    ),
    exclude_owner: str | None = Query(
        default=None,
        description="Owner of the excluded project. Defaults to the caller.",
    ),
    node_limit: int | None = Query(default=None, ge=1, le=MAX_GREP_NODE_LIMIT),
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Exact-pattern search across ingested content.

    Addressed exactly like ``/ls`` — global reads, ``owner``/``all_owners`` to
    widen, a bare ``project`` meaning the caller's own — and the exclusion is
    resolved the same way, so it cannot name a path outside the corpus.

    Returns the backend's own payload. Unlike ``/find`` there is no mapped
    schema: grep results are structural, and inventing one before a consumer
    needs it would be guesswork.
    """
    target = _read_uri(user, project, path, owner=owner, all_owners=all_owners)
    exclude_uri = (
        _read_uri(
            user,
            exclude_project,
            exclude_path,
            owner=exclude_owner,
            path_field="exclude_path",
            project_field="exclude_project",
            owner_field="exclude_owner",
        )
        if exclude_project or exclude_path or exclude_owner
        else None
    )
    # The exclusion has no `all_owners`, so it is always a concrete URI.
    assert not isinstance(exclude_uri, _EveryOwner)

    manager = await resolve_context_manager(db, user)
    try:
        return await manager.grep(
            await _expand_read_target(manager, target),
            pattern,
            case_insensitive=case_insensitive,
            exclude_uri=exclude_uri,
            node_limit=node_limit,
        )
    except QUERY_FAILURES as exc:
        logger.warning("Context grep failed for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager could not run that search.",
        ) from exc

async def _resolve_project(
    db: AsyncSession, user: BerilUser, project: str
) -> UserProject:
    """Find the caller's project by slug, creating it if it doesn't exist.

    Never publishes: a row created here starts private, and a reused row keeps
    its flag. Publishing waits for ``_publish``, after the ingest has actually
    put something in the corpus — a submission that fails validation or has
    every file rejected must not expose a project that has nothing to show.

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


async def _publish(db: AsyncSession, project: UserProject) -> None:
    """Ingest publishes: mark ``project`` public once its content is in the corpus.

    The context corpus is readable by everyone, so a project with content in
    it is public by definition, and ``is_public`` — the one visibility flag,
    which gates the project page and the public listing — is set to match, so
    the project page never hides what ``/find`` already returns.

    Called only once content has landed: at least one file queued, or every
    file skipped because identical content already completed. "Queued" means
    the backend accepted the file, not that indexing finished; a file that
    later fails asynchronously has still published the row. Publishing from
    the status poll instead would tie visibility to whether anyone polls.
    """
    if not project.is_public:
        project.is_public = True
        await db.commit()


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


# A manifest line that withdraws a file rather than ingesting one. The
# manifest reserves a leading ``!`` for directives — ``_parse_manifest``
# refuses a path that starts with one — so a directive is never mistaken for a
# filename, and a manifest written before directives existed never contains
# one by accident.
REMOVE_DIRECTIVE = "!remove"


class _Manifest(NamedTuple):
    """What a submission asks for: files to ingest and files to withdraw."""

    paths: list[str]
    removals: list[str]


def _parse_manifest(manifest_bytes: bytes) -> _Manifest:
    """Read the manifest into sanitized paths to ingest and paths to remove.

    One path per line; blank lines are ignored so a trailing newline is fine.
    Paths are sanitized the same way upload filenames are, and duplicates are
    dropped so a repeated line does not ingest the same file twice.

    ``!remove <relative/path>`` withdraws a file. Re-ingest is otherwise
    add-only: a path *absent* from the manifest is left alone, because absence
    cannot say whether the user meant "delete it" or "leave it" — so removal is
    only ever explicit. Any other ``!`` line is an unknown directive and
    rejected rather than read as a filename. A path both listed and removed
    contradicts itself and is rejected.
    """
    try:
        text = manifest_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The manifest must be UTF-8 text.",
        ) from exc

    paths: list[str] = []
    removals: list[str] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        target = paths
        if line.startswith("!"):
            directive, _, rest = line.partition(" ")
            if directive != REMOVE_DIRECTIVE:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Unknown manifest directive on line {line_no}: {directive!r}",
                )
            line, target = rest.strip(), removals
        relative_path = _safe_relative_path(line) if line else None
        if relative_path is None or relative_path.startswith("!"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid manifest path on line {line_no}: {raw.strip()!r}",
            )
        # Sanitizing *repairs* a path — it drops ``.``/``..`` and empty
        # segments and turns backslashes into slashes. Harmless for a file
        # being added, but a removal deletes: ``!remove ../README.md`` would
        # become ``README.md`` and delete a file the caller never named. So a
        # removal path must already be clean, or the line is rejected.
        if target is removals and relative_path != line:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Removal path on line {line_no} is not a clean relative "
                    f"path: {line!r}. Name the file exactly; '.', '..', "
                    "leading or doubled slashes, and backslashes are not "
                    "accepted in a removal."
                ),
            )
        if relative_path not in target:
            target.append(relative_path)

    both = sorted(set(paths) & set(removals))
    if both:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The manifest both ingests and removes: " + ", ".join(both)
            ),
        )
    if not paths and not removals:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The manifest lists no files.",
        )
    return _Manifest(paths, removals)


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

    Re-ingest is add-only: a path missing from the manifest is left as it
    is. A file is withdrawn only by an explicit ``!remove <path>`` line, which
    deletes it from the backend and records it ``removed``; naming a path the
    project does not hold reports ``not_found`` and does nothing.

    When every file is skipped and no removal acted, nothing was done, so no
    batch exists and ``batch_id`` is ``None``. That is success, not a missing
    handle.
    """
    settings = get_settings()
    manager = await resolve_context_manager(db, user)
    db_project = await _resolve_project(db, user, project)
    target_root = user_target_root(user.orcid_id, db_project.slug)

    archive_bytes = await archive.read()

    relative_paths, removals = _parse_manifest(await manifest.read())
    entries = len(relative_paths) + len(removals)
    if entries > settings.context_max_ingest_files:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                f"Too many files: {entries} "
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
        "Ingesting %d file(s) to %s for user %s (%d unchanged, %d to remove)",
        len(ingest_files),
        target_root,
        user.orcid_id,
        len(skipped),
        len(removals),
    )

    # Removals act only on what this project actually holds: a path whose
    # newest record is absent or already ``removed`` is reported not_found and
    # nothing is sent, which keeps "remove if it exists" idempotent.
    current = await latest_file_statuses(db, db_project.id) if removals else {}
    present = [p for p in removals if current.get(p, INGEST_REMOVED) != INGEST_REMOVED]
    not_found = [
        IngestResult(
            relative_path=p,
            status=INGEST_NOT_FOUND,
            reason="Not present in this project.",
        )
        for p in removals
        if p not in present
    ]
    removed = (
        await manager.remove_files(present, target_root=target_root) if present else []
    )

    results = (
        await manager.insert_files(ingest_files, target_root=target_root)
        if ingest_files
        else ContextIngestResults(results=[], queued=0, failed=0)
    )
    # Publish only once content is in the corpus: something queued, or skipped
    # because identical content already completed here. A removal never
    # publishes — it takes content out.
    if results.queued or skipped:
        await _publish(db, db_project)

    # Record the submission so its progress stays pollable: the context
    # manager expires its own task records and does not track who owns them.
    # Submitted files and attempted removals get rows; skips and not_found do
    # not — neither did anything, and a row would read as an attempt.
    recorded = results.results + removed
    batch_id = None
    if recorded:
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
                for r in recorded
            ],
        )
        batch_id = batch.id

    removal_failures = sum(1 for r in removed if r.status != INGEST_REMOVED)
    return ContextIngestResults(
        results=recorded + skipped + not_found,
        queued=results.queued,
        failed=results.failed + removal_failures,
        skipped=len(skipped),
        removed=len(removed) - removal_failures,
        not_found=len(not_found),
        batch_id=batch_id,
    )


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
    however many others landed. Unfinished work outranks a clean sweep. Then
    ``expired`` outranks ``unknown``: both mean "outcome not confirmed", but
    expired is the stronger claim (the backend will never tell us) where
    unknown may still resolve on a later poll. Neither is a clean sweep — a
    batch is ``completed`` only when every file was *seen* to complete.

    ``skipped`` and ``not_found`` never appear here: neither did anything, so
    neither writes a batch row. They are reported only in the ingest response.
    ``removed`` is a settled outcome like ``completed`` — a batch of removals
    that all succeeded rolls up ``completed``.
    """
    statuses = {f.status for f in files}
    if INGEST_FAILED in statuses:
        return INGEST_FAILED
    if statuses & {INGEST_QUEUED, INGEST_PROCESSING}:
        return INGEST_PROCESSING
    if INGEST_EXPIRED in statuses:
        return INGEST_EXPIRED
    if INGEST_UNKNOWN in statuses:
        return INGEST_UNKNOWN
    return INGEST_COMPLETED
