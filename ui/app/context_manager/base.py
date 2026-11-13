import base64
import hashlib
import mimetypes
import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .addresses import Address, OptionalAddress

# Upper bounds on what a caller may ask the backend for. Not tuning knobs — a
# query is rejected rather than forwarded when it exceeds these, so one request
# cannot ask the backend to walk its whole graph.
MAX_FIND_LIMIT = 200
MAX_FIND_NODE_LIMIT = 10_000
MAX_LS_NODE_LIMIT = 10_000
# How deep a recursive listing may go below its root. Generous on purpose: the
# store's own recursive ``ls`` stops at 3 levels, which hides every fragment of
# a decomposed document; listings are bounded by ``node_limit`` regardless.
MAX_LS_DEPTH = 64
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

# How many per-project memories (pitfalls or discoveries) a by-protocol query
# names as explicit search targets. Past this the search scopes to the narrowest enclosing
# directory instead and filters results by document shape, so a large corpus
# degrades to a broader scan rather than to an oversized request.
MAX_MEMORY_DOCUMENTS = 256


# Where a file's bytes came from. ``context`` is the context store itself,
# used only when what it returned hashes to the bytes BERIL recorded at
# ingest; ``archive`` is the lakehouse copy ``/submit`` wrote, used when the
# store's copy differs, or the path was never ingested (figures never are).
FILE_SOURCE_CONTEXT = "context"
FILE_SOURCE_ARCHIVE = "archive"

# What ``GET /api/context/read`` will hand out of a project. Narrower than the
# ingest allowlist on purpose: this is the wiki's contract (report, metadata,
# errata and the figures the report embeds), and widening it is a decision,
# not a side effect of ingesting more. Memories, reviews and plans stay
# reachable through ``find``/``grep``/``ls``.
READABLE_FILES = frozenset({"REPORT.md", "README.md", "beril.yaml", "CORRECTIONS.md"})
_READABLE_REFUTATION = re.compile(r"REFUTATION_[1-9][0-9]*\.md")
READABLE_FIGURES_DIR = "figures/"


def is_readable_path(path: str) -> bool:
    """Whether ``path`` (relative to a project) may be read whole.

    ``figures/**`` is any file below ``figures/``; a bare ``figures/`` or an
    empty segment is not a file and is refused. Traversal is the caller's to
    reject before this (``target_uri`` does), so only the shape is checked.
    """
    if path in READABLE_FILES or _READABLE_REFUTATION.fullmatch(path):
        return True
    if path.startswith(READABLE_FIGURES_DIR):
        rest = path[len(READABLE_FIGURES_DIR):]
        return bool(rest) and not rest.startswith("/") and not rest.endswith("/") and "//" not in rest
    return False


class ContextFile(BaseModel):
    """One project file, whole, as ``GET /api/context/read`` returns it.

    ``content`` is the file's text when it decodes as UTF-8, else its bytes
    base64-encoded; ``encoding`` says which, so a client can rebuild the exact
    bytes either way (``to_bytes``). ``sha256`` is of those bytes — the
    byte-exactness the wiki checks quotes and offsets against — and ``source``
    says where they came from (see ``FILE_SOURCE_*``). ``modified_at`` is the
    source's own timestamp when it reports one.
    """

    address: str
    owner: str
    project: str
    path: str
    content: str
    encoding: Literal["utf-8", "base64"] = "utf-8"
    sha256: str
    size: int
    content_type: str | None = None
    source: Literal["context", "archive"]
    modified_at: datetime | None = None

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        address: str,
        owner: str,
        project: str,
        path: str,
        source: str,
        content_type: str | None = None,
        modified_at: datetime | None = None,
    ) -> "ContextFile":
        """Wrap raw bytes, choosing the encoding the bytes allow.

        Text is kept as text when it round-trips: a file that decodes as
        strict UTF-8 re-encodes to the same bytes, so ``sha256`` holds either
        way. Anything else is base64.
        """
        try:
            content, encoding = data.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            content, encoding = base64.b64encode(data).decode("ascii"), "base64"
        return cls(
            address=address,
            owner=owner,
            project=project,
            path=path,
            content=content,
            encoding=encoding,
            sha256=hashlib.sha256(data).hexdigest(),
            size=len(data),
            content_type=content_type or mimetypes.guess_type(path)[0],
            source=source,
            modified_at=modified_at,
        )

    def to_bytes(self) -> bytes:
        """The exact bytes ``sha256`` was computed over."""
        if self.encoding == "base64":
            return base64.b64decode(self.content)
        return self.content.encode("utf-8")


class ContextFileNotFound(LookupError):
    """No copy of the file exists anywhere ``get_file`` looks."""


class ArchiveUnavailableError(RuntimeError):
    """The lakehouse archive could not be asked — unconfigured, unreachable,
    or refusing the credentials. Distinct from a missing file."""

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
# Explicitly withdrawn by a ``!remove`` manifest entry and deleted from the
# backend. Terminal, and recorded as the path's newest row, so it supersedes
# any earlier ``completed``: the skip check no longer matches (a re-added file
# is re-sent) and the project no longer counts as owning that memory.
INGEST_REMOVED = "removed"
# A ``!remove`` named a path this project never ingested, or already removed.
# Response-only, like ``skipped``: nothing was done, so no row is written.
INGEST_NOT_FOUND = "not_found"

# How a batch came to exist, recorded on ``context_ingest_batch.kind`` and
# served by the submissions feed. ``approved`` is a ``/submit`` ingest — it
# passed the approval gate; ``seeded`` is an admin import of a repo project
# that predates ``/submit``; ``retirement`` is the bookkeeping batch an import
# writes for a re-owned project's old copies, never a submission.
INGEST_KIND_APPROVED = "approved"
INGEST_KIND_SEEDED = "seeded"
INGEST_KIND_RETIREMENT = "retirement"
SUBMISSION_KINDS = (INGEST_KIND_APPROVED, INGEST_KIND_SEEDED)

TERMINAL_INGEST_STATUSES = frozenset(
    {INGEST_COMPLETED, INGEST_FAILED, INGEST_EXPIRED, INGEST_SKIPPED, INGEST_REMOVED}
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
    INGEST_REMOVED,
    INGEST_NOT_FOUND,
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
    # ``uri`` holds the backend URI internally and leaves as ``address``
    # (see ``addresses``); populate_by_name keeps ``uri=`` constructors.
    model_config = ConfigDict(populate_by_name=True)

    uri: OptionalAddress = Field(default=None, alias="address")
    reason: str | None = None
    task_id: str | None = None


class ContextIngestResults(BaseModel):
    """Outcome of one submission. ``batch_id`` is the handle for polling it.

    ``batch_id`` is ``None`` when nothing was submitted or removed — every
    file was skipped as unchanged and every removal named a path not present,
    so no batch exists and there is nothing to poll. Callers must treat that
    as success, not as a missing handle.
    """
    results: list[IngestResult]
    queued: int
    failed: int
    skipped: int = 0
    removed: int = 0
    not_found: int = 0
    batch_id: str | None = None


class ContextImportResults(ContextIngestResults):
    """An admin import: the ingest outcome, plus whose project it landed in.

    ``dry_run`` results carry only ``project`` and ``owner_orcid`` — the owner
    an import *would* write under — and nothing was read or written.
    """

    project: str
    owner_orcid: str
    dry_run: bool = False
    # Files still held in a previous owner's namespace (the project was
    # re-owned): each is marked removal-pending and must be retired, one per
    # call, with ``POST /api/admin/context/retire_file/{record_id}``.
    retire_records: list[str] = Field(default_factory=list)


class IngestFileStatus(BaseModel):
    relative_path: str
    status: str
    # ``uri`` holds the backend URI internally and leaves as ``address``
    # (see ``addresses``); populate_by_name keeps ``uri=`` constructors.
    model_config = ConfigDict(populate_by_name=True)

    uri: OptionalAddress = Field(default=None, alias="address")
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

    The time bounds are checked here against the store's own grammar (see
    ``check_time_bound``), so a malformed one is a 422 naming the field rather
    than a backend rejection that can only surface as an opaque 502.

    ``read_content`` asks for each hit's full text, not just its abstract. It
    is off by default because a broad query would otherwise return every
    matching document in full.

    ``limit`` is how many results come back, at most — the best-ranked ones.
    ``node_limit`` is how many backend nodes the search may rank to find them;
    omitted, it is set wider than ``limit`` (see ``OpenVikingManager.query``).
    Raising it widens the search, never the number returned.
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

    @field_validator("since", "until")
    @classmethod
    def _time_bound(cls, value: str | None) -> str | None:
        return None if value is None else check_time_bound(value)


# The store's time-bound grammar (openviking.utils.search_filters, identical in
# 0.4.15 and 0.4.22): a relative amount — seconds, minutes, hours, days or
# weeks before now — a date, or an ISO 8601 datetime. ``m`` is minutes; there
# is no month or year unit.
_RELATIVE_BOUND = re.compile(r"\d+[smhdw]")
_DATE_BOUND = re.compile(r"\d{4}-\d{2}-\d{2}")
TIME_BOUND_FORMS = (
    "a relative amount like 30m, 12h, 7d or 2w (s, m = minutes, h, d, w; "
    "no month or year unit), a date like 2026-01-31, or an ISO 8601 datetime"
)


def check_time_bound(value: str) -> str:
    """Return ``value`` if the store can read it as a time bound, else raise.

    Mirrors the store's own parser, which accepts a relative amount, a
    ``YYYY-MM-DD`` date, or anything ``datetime.fromisoformat`` reads (with a
    trailing ``Z`` for UTC). Checked here because the store's rejection could
    only surface as a 502 the caller cannot tell from an outage.
    """
    value = value.strip()
    if _RELATIVE_BOUND.fullmatch(value):
        return value
    if _DATE_BOUND.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            pass
    else:
        try:
            datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
            return value
        except ValueError:
            pass
    raise ValueError(f"not a recognized time bound; use {TIME_BOUND_FORMS}")


class QueryResult(BaseModel):
    """One hit.

    ``text`` is the abstract — a summary, not the document. ``content`` carries
    the full text and is present only when the query asked for it, so an absent
    ``content`` means "not requested", never "empty document".
    """

    # ``uri`` holds the backend URI internally and leaves as ``address``
    # (see ``addresses``); populate_by_name keeps ``uri=`` constructors.
    model_config = ConfigDict(populate_by_name=True)

    uri: Address = Field(alias="address")
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

    # ``uri`` holds the backend URI internally and leaves as ``address``
    # (see ``addresses``); populate_by_name keeps ``uri=`` constructors.
    model_config = ConfigDict(populate_by_name=True)

    uri: Address = Field(alias="address")
    origin: Literal["project_memory", "central"]
    project: str | None = None
    owner: str | None = None
    # ``None`` when nothing was searched — a listing has no relevance to rank.
    score: float | None = None
    excerpts: list[str] = Field(default_factory=list)
    fragment_uris: list[Address] = Field(
        default_factory=list, alias="fragment_addresses"
    )


class PitfallResults(BaseModel):
    """Pitfall documents: matches for a query, best first — or, with no
    query, every pitfall document in scope.

    ``fragments_scanned`` is how many matching pitfall fragments there were
    before grouping — reported so a caller can tell a broad query from a
    narrow one without the route inventing a relevance judgement. It is 0 for
    a listing, which searches nothing.

    ``total`` is how many documents qualified before ``limit`` was applied, so
    a caller can tell a short list from a truncated one.
    """

    query: str | None = None
    results: list[PitfallHit]
    fragments_scanned: int = 0
    total: int = 0


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

    # ``uri`` holds the backend URI internally and leaves as ``address``
    # (see ``addresses``); populate_by_name keeps ``uri=`` constructors.
    model_config = ConfigDict(populate_by_name=True)

    uri: Address = Field(alias="address")
    origin: Literal["project_memory", "central_legacy", "central_background"]
    project: str | None = None
    owner: str | None = None
    # ``None`` when nothing was searched — a listing has no relevance to rank.
    score: float | None = None
    excerpts: list[str] = Field(default_factory=list)
    fragment_uris: list[Address] = Field(
        default_factory=list, alias="fragment_addresses"
    )


class DiscoveryResults(BaseModel):
    """Discoveries matching a query, deduplicated, best first — or, with no
    query, every discovery document in scope.

    ``suppressed`` counts stale central duplicates dropped by the precedence
    rule — reported rather than hidden so a caller can tell "nothing matched"
    from "the current copy answered instead". ``total`` is how many documents
    survived precedence before ``limit`` was applied.
    """

    query: str | None = None
    results: list[DiscoveryHit]
    fragments_scanned: int = 0
    suppressed: int = 0
    total: int = 0


class ContextQueryResults(BaseModel):
    """``total`` is how many results the search reached before they were
    trimmed to the query's ``limit``. More than ``len(results)`` means more
    ranked results exist past the limit; it is not a count of every match — a
    semantic search ranks the whole scope, it does not filter it."""

    query: str
    results: list[QueryResult]
    total: int = 0

class ContextManager:
    url: str
    config: dict[str, str]

    async def get_file(
        self, address: str, *, expected_sha256: str | None
    ) -> ContextFile:
        """One project file, whole and byte-exact.

        ``address`` is ``<owner>/<project>/<path>``. ``expected_sha256`` is
        the hash BERIL recorded when the path last completed an ingest, or
        ``None`` when it never did; it decides whether the store's copy may
        be served (see ``OpenVikingManager.get_file``). Raises
        ``ContextFileNotFound`` when no source has the file.
        """
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

    async def list_files(self, uri: str | list[str], **options) -> list:
        ...

    async def query(
        self, query: ContextQuery, *, target_uri: str | list[str]
    ) -> ContextQueryResults:
        """Search below ``target_uri`` — one location, or several searched as
        one. The route resolves the query's addressing into the target; the
        manager never derives it from the query itself."""

