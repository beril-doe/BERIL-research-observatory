from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# Upper bounds on what a caller may ask the backend for. Not tuning knobs — a
# query is rejected rather than forwarded when it exceeds these, so one request
# cannot ask the backend to walk its whole graph.
MAX_FIND_LIMIT = 200
MAX_FIND_NODE_LIMIT = 10_000
MAX_LS_NODE_LIMIT = 10_000
MAX_GREP_NODE_LIMIT = 10_000
MAX_PITFALL_LIMIT = 50
MAX_DISCOVERY_LIMIT = 50

# The backend's own per-call defaults (server 0.4.22, and the SDK fills them in
# when a caller omits node_limit). A read that fans out over several owners
# uses these as the budget for the whole request, so omitting node_limit
# returns no more than a single-location read would.
DEFAULT_LS_NODE_LIMIT = 1000
DEFAULT_GREP_NODE_LIMIT = 256

# How many owners' copies of one project a single read may expand to. Past
# this the read is refused rather than silently narrowed to a subset — the
# caller is asked to name an owner instead.
MAX_OWNER_EXPANSION = 256


class FileMetadata(BaseModel):
    created: datetime
    owner: str
    last_changed: datetime
    path: Path

class ContextFile(BaseModel):
    """
    A class representing a file stored in the context manager.
    """
    content: str
    metadata: FileMetadata

class ContextIngestFile(BaseModel):
    """One file bound for the context manager.

    ``relative_path`` may contain ``/`` — a directory upload keeps its structure
    below the ingest root. It is expected to be sanitized by the caller.
    ``content`` is raw bytes so binary files (notebooks, PDFs, images) ingest
    the same way text does.
    """
    relative_path: str
    content: bytes
    content_type: str | None = None


# BERIL's own ingest vocabulary, deliberately independent of any backend's task
# states so the status API survives swapping the context manager.
INGEST_QUEUED = "queued"
INGEST_PROCESSING = "processing"
INGEST_COMPLETED = "completed"
INGEST_FAILED = "failed"
# The backend forgot the task before we saw it finish. It expires task records
# (24h completed / 7d failed), so once a poll stops before completion and the
# record ages out, the outcome is unrecoverable from the task alone. Terminal:
# re-polling can never learn more. NOT a success — the file may well have
# landed, but nothing here proves it, so a later ingest treats it as unknown
# content and re-sends. Reconciling against the store itself (does the target
# URI exist?) is the follow-up that would restore the skip.
INGEST_EXPIRED = "expired"
# Could not reach the backend to ask. Transient: the task is still there and a
# later poll may resolve it, so the status route keeps what it last recorded
# rather than overwriting it with this.
INGEST_UNKNOWN = "unknown"
# Identical content already completed for this project, so nothing was sent.
# Reported per-file rather than silently omitted: a missing file in the response
# is indistinguishable from a bug when the user's file doesn't turn up.
INGEST_SKIPPED = "skipped"

TERMINAL_INGEST_STATUSES = frozenset(
    {INGEST_COMPLETED, INGEST_FAILED, INGEST_EXPIRED, INGEST_SKIPPED}
)

# Every status, in lifecycle order — used to render a stable counts mapping.
INGEST_STATUSES = (
    INGEST_QUEUED,
    INGEST_PROCESSING,
    INGEST_COMPLETED,
    INGEST_FAILED,
    INGEST_EXPIRED,
    INGEST_UNKNOWN,
    INGEST_SKIPPED,
)


class IngestResult(BaseModel):
    """Per-file outcome of a submission.

    ``queued`` means the context manager accepted the file for processing, not
    that it is searchable yet — indexing completes asynchronously. ``task_id``
    is the backend handle used to poll that progress, absent when the
    submission itself failed.
    """
    relative_path: str
    status: str
    uri: str | None = None
    reason: str | None = None
    task_id: str | None = None


class ContextIngestResults(BaseModel):
    """Outcome of one submission. ``batch_id`` is the handle for polling it.

    ``batch_id`` is ``None`` when nothing was submitted — every file was
    skipped as unchanged, so no batch exists and there is nothing to poll.
    Callers must treat that as success, not as a missing handle.
    """
    results: list[IngestResult]
    queued: int
    failed: int
    skipped: int = 0
    batch_id: str | None = None


class IngestFileStatus(BaseModel):
    relative_path: str
    status: str
    uri: str | None = None
    error: str | None = None


class IngestBatchStatus(BaseModel):
    """Rolled-up progress of one submission."""
    batch_id: str
    project: str
    status: str
    counts: dict[str, int]
    files: list[IngestFileStatus]


class ContextQuery(BaseModel):
    """One semantic search against the context layer.

    Scope is addressed the same way ``ls`` and ``grep`` are — by ``project``
    (a slug), ``owner`` (an ORCiD, defaulting to the caller), ``all_owners``,
    and an optional ``path`` below the project — never by a raw backend URI.
    The route resolves those into the target the manager searches, so a caller
    cannot name a location outside the corpus.

    The time bounds accept whatever the backend accepts (an ISO date, or a
    relative form like ``7d``); they are validated as non-empty strings here
    and interpreted downstream, so a malformed bound is the backend's to
    reject.

    ``read_content`` asks for each hit's full text, not just its abstract. It
    is off by default because a broad query would otherwise return every
    matching document in full.
    """

    query: str
    project: str | None = None
    owner: str | None = None
    all_owners: bool = False
    path: str | None = None
    limit: int = Field(default=10, ge=1, le=MAX_FIND_LIMIT)
    score_threshold: float | None = None
    since: str | None = None
    until: str | None = None
    time_field: Literal["updated_at", "created_at"] | None = None
    node_limit: int | None = Field(default=None, ge=1, le=MAX_FIND_NODE_LIMIT)
    read_content: bool = False


class QueryResult(BaseModel):
    """One hit.

    ``text`` is the abstract — a summary, not the document. ``content`` carries
    the full text and is present only when the query asked for it, so an absent
    ``content`` means "not requested", never "empty document".
    """

    uri: str
    context_type: str
    score: float
    text: str
    match_reason: str | None = None
    content: str | None = None


class PitfallHit(BaseModel):
    """One pitfall document, with the fragments that matched inside it.

    The backend decomposes a document into many nodes, so a raw search returns
    fragments of the same file as separate hits. Grouping them here means a
    caller sees documents — which is the unit a user reads and cites.

    ``origin`` says which half of the corpus it came from: ``project_memory``
    for ``projects/<id>/memories/pitfalls.md``, ``central`` for the shared
    archive. ``project`` is the owning project when known, and ``None`` for a
    central doc that names no project.
    """

    uri: str
    origin: Literal["project_memory", "central"]
    project: str | None = None
    owner: str | None = None
    score: float
    excerpts: list[str] = Field(default_factory=list)
    fragment_uris: list[str] = Field(default_factory=list)


class PitfallResults(BaseModel):
    """Documents matching a pitfall query, best first.

    ``fragments_scanned`` is how many raw nodes the backend returned before
    grouping — reported so a caller can tell a broad query from a narrow one
    without the route inventing a relevance judgement.
    """

    query: str | None = None
    results: list[PitfallHit]
    fragments_scanned: int = 0


class DiscoveryHit(BaseModel):
    """One discovery document.

    ``origin`` is the precedence class, not merely a location:

    * ``project_memory`` — review-vetted, current. Written at ``/submit``
      approval, so it is approved findings by construction.
    * ``central_legacy`` — a central entry tagged for a project that has no
      per-project memory, i.e. predating the per-project pattern.
    * ``central_background`` — an untagged central entry, belonging to no
      project.

    A central entry tagged for a project that *does* have its own memory is a
    stale duplicate and never appears — see ``PROJECT_MEMORY_WINS``.
    """

    uri: str
    origin: Literal["project_memory", "central_legacy", "central_background"]
    project: str | None = None
    owner: str | None = None
    score: float
    excerpts: list[str] = Field(default_factory=list)
    fragment_uris: list[str] = Field(default_factory=list)


class DiscoveryResults(BaseModel):
    """Discoveries matching a query, deduplicated, best first.

    ``suppressed`` counts stale central duplicates dropped by the precedence
    rule — reported rather than hidden so a caller can tell "nothing matched"
    from "the current copy answered instead".
    """

    query: str | None = None
    results: list[DiscoveryHit]
    fragments_scanned: int = 0
    suppressed: int = 0


class ContextQueryResults(BaseModel):
    """``total`` is the backend's own count, which may exceed ``len(results)``
    when the query was limited."""

    query: str
    results: list[QueryResult]
    total: int = 0

class ContextManager:
    url: str
    config: dict[str, str]

    async def get_file(self, path: Path) -> ContextFile:
        ...

    async def insert_file(
        self, file: ContextIngestFile, *, target_root: str
    ) -> IngestResult:
        """Ingest a single file below ``target_root``. Never raises."""
        ...

    async def insert_files(
        self, files: list[ContextIngestFile], *, target_root: str
    ) -> ContextIngestResults:
        """Ingest a batch below ``target_root``.

        Each file succeeds or fails independently — one bad file does not
        abort the rest of the batch.
        """
        ...

    async def list_files(self) -> list[ContextFile]:
        ...

    async def query(
        self, query: ContextQuery, *, target_uri: str | list[str]
    ) -> ContextQueryResults:
        """Search below ``target_uri`` — one location, or several searched as
        one. The route resolves the query's addressing into the target; the
        manager never derives it from the query itself."""

