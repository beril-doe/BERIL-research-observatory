from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

# Upper bounds on what a caller may ask the backend for. Not tuning knobs — a
# query is rejected rather than forwarded when it exceeds these, so one request
# cannot ask the backend to walk its whole graph.
MAX_FIND_LIMIT = 200
MAX_FIND_NODE_LIMIT = 10_000


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
# The backend forgot the task before we saw it finish — we genuinely don't know.
INGEST_UNKNOWN = "unknown"
# Identical content already completed for this project, so nothing was sent.
# Reported per-file rather than silently omitted: a missing file in the response
# is indistinguishable from a bug when the user's file doesn't turn up.
INGEST_SKIPPED = "skipped"

TERMINAL_INGEST_STATUSES = frozenset(
    {INGEST_COMPLETED, INGEST_FAILED, INGEST_SKIPPED}
)

# Every status, in lifecycle order — used to render a stable counts mapping.
INGEST_STATUSES = (
    INGEST_QUEUED,
    INGEST_PROCESSING,
    INGEST_COMPLETED,
    INGEST_FAILED,
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

    ``filter`` is a backend metadata filter tree, passed through as given —
    callers that need one are already reaching past the simple case. The time
    bounds accept whatever the backend accepts (an ISO date, or a relative form
    like ``7d``); they are validated as non-empty strings here and interpreted
    downstream, so a malformed bound is the backend's to reject.

    ``read_content`` asks for each hit's full text, not just its abstract. It
    is off by default because a broad query would otherwise return every
    matching document in full.
    """

    query: str
    root_path: str | None = None
    limit: int = Field(default=10, ge=1, le=MAX_FIND_LIMIT)
    score_threshold: float | None = None
    filter: dict[str, Any] | None = None
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

    async def query(self, query: ContextQuery) -> ContextQueryResults:
        ...

