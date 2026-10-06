import asyncio
import fnmatch
import logging
import re
import tempfile
from pathlib import Path

import httpx
from openviking_sdk.errors import NotFoundError as SdkNotFoundError
from openviking_sdk.errors import OpenVikingError as SdkOpenVikingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.openviking import (
    OpenVikingClient,
    OpenVikingError,
    regenerate_ov_user_key,
    register_ov_user,
)
from app.config import Settings, get_settings
from app.crypto import decrypt_secret, encrypt_secret
from app.db.crud import get_ov_credential, upsert_ov_credential
from app.db.models import BerilUser

from .base import (
    DEFAULT_GREP_NODE_LIMIT,
    DEFAULT_LS_NODE_LIMIT,
    INGEST_COMPLETED,
    INGEST_EXPIRED,
    INGEST_FAILED,
    INGEST_PROCESSING,
    INGEST_QUEUED,
    INGEST_UNKNOWN,
    MAX_MEMORY_DOCUMENTS,
    ContextFile,
    ContextIngestFile,
    ContextIngestResults,
    ContextManager,
    ContextQuery,
    ContextQueryResults,
    IngestResult,
    QueryResult,
)

logger = logging.getLogger(__name__)

# Expected per-file ingest failures: anything the OV SDK raises, the disk spill
# failing, or the transport dropping. Deliberately not bare Exception — a bug in
# our own code should surface, not be reported as a rejected file.
INGEST_FAILURES: tuple[type[Exception], ...] = (
    SdkOpenVikingError,
    OSError,
    httpx.HTTPError,
    # An unsafe path caught at the spill — recorded against the file rather
    # than raised, so one bad name cannot abort the batch.
    ValueError,
)

# Expected read-path failures: the backend rejecting a query, or the transport
# dropping. Named here rather than in the routes so the backend's exception
# types stay inside this module — a route catching SdkOpenVikingError would put
# the store's name back in the layer that exists to hide it. Deliberately not
# bare Exception: a bug in our own mapping code should surface as a 500.
QUERY_FAILURES: tuple[type[Exception], ...] = (
    SdkOpenVikingError,
    OpenVikingError,
    httpx.HTTPError,
)

# OpenViking's six task states collapsed onto BERIL's four. "cancelling" is
# reported as processing because BERIL exposes no cancel, and "cancelled" as
# failed because the file did not land either way.
_OV_STATUS_MAP = {
    "pending": INGEST_QUEUED,
    "running": INGEST_PROCESSING,
    "cancelling": INGEST_PROCESSING,
    "completed": INGEST_COMPLETED,
    "failed": INGEST_FAILED,
    "cancelled": INGEST_FAILED,
}

USERS_TARGET_URI = "viking://resources/users/"

# The backend's own shape for a grep that matched nothing (verified against
# server 0.4.22). Returned, rather than invented, when there is nowhere to
# search, so a consumer sees one shape whether or not the backend was asked.
_EMPTY_GREP: dict = {"matches": [], "count": 0, "match_count": 0, "files_scanned": 0}

# The house account: central docs (pitfalls, discoveries, performance,
# research_ideas) have no owner, so they live under a reserved name in the same
# per-user tree rather than needing an ownerless special case in every read.
#
# Reserved, not merely conventional: ``BerilUser.orcid_id`` is an unvalidated
# String(64), so without this guard a row carrying orcid_id="beril" would own
# the shared central docs and be able to rewrite them. Distinct from
# ``settings.ov_account_id`` (also "beril"), which appears in a different part
# of the URI — the admin path, not a namespace segment.
HOUSE_ACCOUNT_ID = "beril"


class ReservedNamespaceError(ValueError):
    """Raised when a user's identity would claim the house namespace."""


def context_slugify(name: str) -> str:
    """Normalize a project name into a url-safe, underscore-separated slug.

    Distinct from ``routes.data._slugify``, which hyphenates for web URLs.
    The context namespace uses underscores to match the on-disk ``projects/``
    layout. An already-valid slug passes through unchanged. Returns ``""`` when
    nothing usable survives, which callers must reject.
    """
    slug = re.sub(r"[^\w\s-]", "", name.strip().lower())
    slug = re.sub(r"[\s-]+", "_", slug)
    return slug.strip("_")


def user_target_root(orcid_id: str, project_slug: str) -> str:
    """The ingest root for one user's project.

    Keyed on ORCiD rather than project slug alone so two users' identically
    named projects never share a namespace.

    Refuses the house account: a user whose ORCiD is the reserved name would
    otherwise be able to write the shared central docs. Checked here rather
    than only at user creation so an already-stored row cannot reach it.
    """
    if orcid_id == HOUSE_ACCOUNT_ID:
        raise ReservedNamespaceError(
            f"{HOUSE_ACCOUNT_ID!r} is reserved for BERIL's own central docs."
        )
    return f"{USERS_TARGET_URI}{orcid_id}/{project_slug}"


def user_namespace_root(orcid_id: str) -> str:
    """Everything one user has ingested, across all their projects."""
    return f"{USERS_TARGET_URI}{orcid_id}"


def corpus_root() -> str:
    """Every owner's namespace — the root of readable content.

    Reads span this; writes never do. A submitted project is owned by one user
    but readable by all, so the read boundary is the tree root while the write
    boundary stays the owner's ORCiD.
    """
    return USERS_TARGET_URI.rstrip("/")


def listing_uri(
    owner_id: str | None = None,
    project_slug: str | None = None,
    relative_path: str | None = None,
) -> str:
    """Resolve a read target within the corpus.

    Reads are global: a submitted project is owned by one user and readable by
    everyone, like a public repository. ``owner_id`` therefore narrows the
    target rather than authorizing it — omit it to span every owner.

    The boundary is the corpus root, not the owner: a relative path may not
    climb out of ``resources/users/`` into the wider resource tree. Traversal
    is rejected rather than normalized, so ``..`` cannot be used to probe
    outside the corpus.

    This is the asymmetric half of the model. The *write* path
    (``user_target_root``) stays pinned to the authenticated ORCiD; only reads
    are unscoped. Callers must not route a write through here.

    Raises ``ValueError`` on traversal, or on a ``project_slug`` or
    ``relative_path`` given without an owner to hang it on — a project name
    alone does not identify a resource when every owner may have one.
    """
    if (project_slug or relative_path) and not owner_id:
        raise ValueError("A project or path requires an owner.")

    root = corpus_root()
    if not owner_id:
        return root
    # The owner segment is itself untrusted when it comes from a caller
    # (``?owner=``), so it goes through the same traversal check as the path.
    segments = [owner_id]
    if project_slug:
        segments.append(project_slug)
    if relative_path:
        segments.append(relative_path)
    return target_uri(root, "/".join(segments))


def target_uri(target_root: str, relative_path: str) -> str:
    """Join an ingest root and a sanitized relative path into a target URI.

    The relative path is sanitized upstream; the traversal check here is
    defense in depth, since a ``..`` segment reaching OpenViking would write
    outside the user's namespace.
    """
    segments = [s for s in relative_path.replace("\\", "/").split("/") if s]
    if not segments or any(s in {".", ".."} for s in segments):
        raise ValueError(f"Unsafe relative path: {relative_path!r}")
    return f"{target_root.rstrip('/')}/{'/'.join(segments)}"


# The backend decomposes each document into a tree, turning section headings
# into path segments and appending a content hash, so one source file yields
# many nodes. It also synthesizes two kinds of node that are structure rather
# than content:
#
#   .overview.md — a directory stub, usually "[Directory overview is not
#                  generated]"
#   .abstract.md — a generated summary that restates its parent
#
# Both match a semantic query readily and neither is a pitfall, so they are
# dropped before results reach a caller.
_SYNTHETIC_NODES = (".overview.md", ".abstract.md")


def is_synthetic_node(uri: str) -> bool:
    """True when ``uri`` is a backend-generated stub rather than content."""
    return uri.rsplit("/", 1)[-1] in _SYNTHETIC_NODES


def source_document(uri: str, corpus_root: str) -> str:
    """The source document a fragment came from.

    The two halves of the corpus nest differently, so this cannot key on one
    rule:

    * a project memory is a file, and its fragments hang below it —
      ``…/<project>/memories/pitfalls.md/<chunk>.md``, so the first ``.md``
      segment is the document;
    * a central doc is decomposed under its *slug directory* —
      ``…/beril/docs/<slug>/<slug>/<Section>/<chunk>.md``, where every segment
      including the leaf ends in ``.md``, so the first-``.md`` rule would
      return the fragment itself and collapse nothing.

    Central docs are therefore cut at the slug directory, which is the unit a
    caller reads and cites. Returns ``uri`` unchanged when neither shape
    matches — better to report the node than to guess at a grouping.
    """
    if not uri.startswith(corpus_root):
        return uri
    segments = uri[len(corpus_root):].strip("/").split("/")

    def _join(count: int) -> str:
        return f"{corpus_root.rstrip('/')}/{'/'.join(segments[:count])}"

    # Central doc: <owner>/docs/<slug>/…
    if len(segments) >= 3 and segments[0] == HOUSE_ACCOUNT_ID and segments[1] == "docs":
        return _join(3)

    # Project memory: the first .md segment is the file itself.
    for index, segment in enumerate(segments):
        if segment.endswith(".md"):
            return _join(index + 1)
    return uri


def _glob_match(relative: str, pattern: str) -> bool:
    """Shell-style match, segment by segment, like the backend's glob.

    ``fnmatch`` alone lets ``*`` cross ``/``, so ``*/*/memories/pitfalls.md``
    would also match a file nested deeper; matching per segment keeps it to
    exactly the shape the pattern names.
    """
    parts, wanted = relative.split("/"), pattern.split("/")
    return len(parts) == len(wanted) and all(
        fnmatch.fnmatchcase(part, want) for part, want in zip(parts, wanted, strict=True)
    )


def _grep_nodes(payload: dict) -> list[dict]:
    """Normalize a grep payload onto the same node shape ``find`` produces.

    Grep returns ``{"matches": [{"line", "uri", "content"}]}`` and carries no
    relevance score, so every match scores 1.0 — an exact hit is an exact hit,
    and ranking them against each other would invent a judgement the backend
    did not make. Ordering then falls to match count, which ``_collapse_``
    ``fragments`` applies.
    """
    return [
        {
            "uri": match.get("uri") or "",
            "score": 1.0,
            "text": (match.get("content") or "").strip(),
        }
        for match in (payload.get("matches") or [])
    ]


def _collapse_fragments(nodes: list[dict], *, limit: int) -> list[dict]:
    """Group fragment nodes by source document, best score first.

    One document yields many fragments, so returning nodes directly floods a
    caller with pieces of the same file. A document's score is its best
    fragment's: a strong match anywhere in a pitfall entry makes that entry
    worth reading, and averaging would bury a precise hit inside a long doc.

    Synthetic nodes are dropped first — they match readily and say nothing.
    """
    corpus = USERS_TARGET_URI
    documents: dict[str, dict] = {}
    for node in nodes:
        uri = node.get("uri") or ""
        if not uri or is_synthetic_node(uri):
            continue
        doc_uri = source_document(uri, corpus)
        entry = documents.setdefault(
            doc_uri,
            {"uri": doc_uri, "score": 0.0, "excerpts": [], "fragment_uris": []},
        )
        entry["score"] = max(entry["score"], float(node.get("score") or 0.0))
        entry["fragment_uris"].append(uri)
        text = (node.get("text") or "").strip()
        # Keep a few excerpts, not every fragment: enough to judge relevance
        # without returning the document twice over.
        if text and len(entry["excerpts"]) < 3 and text not in entry["excerpts"]:
            entry["excerpts"].append(text)

    ranked = sorted(
        documents.values(),
        # Score first; then match count, which is the only signal grep gives.
        key=lambda d: (d["score"], len(d["fragment_uris"])),
        reverse=True,
    )
    return ranked[:limit]


# A central discovery entry names its project inline, as ``[<project_id>]`` —
# in an ``### [tag] Title`` heading centrally, and in an HTML-comment
# provenance line in a per-project memory. Project ids are the slug shape
# ``context_slugify`` produces.
_PROJECT_TAG = re.compile(r"\[([a-z0-9][a-z0-9_]*)\]")

# The precedence rule, quoted from `suggest-research` Step 4 so the two cannot
# drift silently:
#
#   per-project memory wins. If a project has any per-project
#   memories/discoveries.md, suppress matches in docs/discoveries.md tagged
#   with that same [<project_id>] (those are stale duplicates the project
#   already owns). Central entries tagged with project ids that have NO
#   per-project memory are still considered (legacy projects). Untagged
#   central entries are background context — always included.
PROJECT_MEMORY_WINS = True


def project_tags(text: str) -> set[str]:
    """Every ``[<project_id>]`` tag named in ``text``."""
    return set(_PROJECT_TAG.findall(text or ""))


def apply_discovery_precedence(
    documents: list[dict], *, projects_with_memory: set[str]
) -> tuple[list[dict], int]:
    """Classify discoveries and drop stale central duplicates.

    Returns ``(kept, suppressed_count)``. Implements the three-way rule once,
    server-side, instead of leaving each caller to re-read it from prose and
    get it slightly wrong.

    A central entry is suppressed only when it names a project that has its own
    memory — the project owns the current copy. A central entry naming a
    project with no memory is legacy content and still counts; an untagged one
    is background and always counts.
    """
    kept: list[dict] = []
    suppressed = 0
    for doc in documents:
        uri = doc.get("uri") or ""
        segments = uri.removeprefix(USERS_TARGET_URI).strip("/").split("/")
        owner = segments[0] if segments else None

        if owner != HOUSE_ACCOUNT_ID:
            # A project's own memory: current by construction.
            kept.append(
                {
                    **doc,
                    "origin": "project_memory",
                    "project": segments[1] if len(segments) > 1 else None,
                    "owner": owner,
                }
            )
            continue

        # Central. Its tags decide whether a project already owns this content.
        tags = project_tags(" ".join(doc.get("excerpts") or []))
        stale = tags & projects_with_memory
        if stale:
            suppressed += 1
            continue
        kept.append(
            {
                **doc,
                "origin": "central_legacy" if tags else "central_background",
                # Report one tag when the entry names exactly one project;
                # several tags make "the" project meaningless.
                "project": next(iter(tags)) if len(tags) == 1 else None,
                "owner": owner,
            }
        )
    return kept, suppressed


class _Budget:
    """One node budget spent across a fan-out of backend calls.

    A single-location read is passed through untouched — ``node_limit`` as the
    caller gave it, omitted when they omitted it — so the backend's own
    default applies exactly as before. Across several locations the limit is
    shared: each call is asked for what remains, and ``take`` trims a result
    to it in case the backend returns more than asked.
    """

    def __init__(self, node_limit: int | None, default: int, *, single: bool):
        self.single = single
        self._given = node_limit
        self.remaining = node_limit if node_limit is not None else default

    @property
    def spent(self) -> bool:
        return not self.single and self.remaining <= 0

    def for_call(self) -> int | None:
        return self._given if self.single else self.remaining

    def take(self, items: list) -> list:
        if self.single:
            return items
        kept = items[: self.remaining]
        self.remaining -= len(kept)
        return kept


class UnauthenticatedError(RuntimeError):
    """Raised when a context-manager call is made without an identified user."""


class OvProvisioningError(RuntimeError):
    """Raised when a user's OpenViking credential can't be obtained or minted."""


class OpenVikingManager(ContextManager):
    def __init__(self, settings: Settings, api_key: str):
        self.url = settings.ov_url
        self.api_key = api_key

    async def get_file(self, path: Path) -> ContextFile:
        ...

    async def insert_files(
        self, files: list[ContextIngestFile], *, target_root: str
    ) -> ContextIngestResults:
        """Ingest a batch, reusing one client for the whole run.

        Files are submitted one at a time — each keeps its own relative path
        below ``target_root``, so they cannot be collapsed into a single
        directory upload. A failure is recorded against that file and the
        batch continues.
        """
        if not files:
            return ContextIngestResults(results=[], queued=0, failed=0)

        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            results = [
                await self._insert_one(ov_client, file, target_root) for file in files
            ]
        finally:
            await ov_client.close()

        queued = sum(1 for r in results if r.status == INGEST_QUEUED)
        return ContextIngestResults(
            results=results, queued=queued, failed=len(results) - queued
        )

    async def task_statuses(self, task_ids: list[str]) -> dict[str, tuple[str, str | None]]:
        """Look up the current status of each task id.

        Returns ``{task_id: (status, error)}`` in BERIL's vocabulary. Two
        non-answers are kept distinct because they call for opposite
        reactions:

        * the backend **could not be asked** (transport or SDK error) →
          ``unknown``. Transient; the caller keeps its last recording and a
          later poll may resolve it.
        * the backend **no longer has the task** (``get_task`` → ``None``, the
          record aged out) → ``expired``. Permanent; re-polling can never
          learn more, so it is terminal and the caller stops asking.

        Conflating them left rows stuck non-terminal forever: an expired task
        reported ``unknown``, the status route discarded ``unknown``, and the
        row was re-polled on every call with no way to ever advance.

        Never raises: a backend that is unreachable mid-poll yields ``unknown``
        for every id, so the caller falls back to what it already recorded
        instead of failing the request.
        """
        if not task_ids:
            return {}

        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            tasks = await asyncio.gather(
                *(ov_client.get_task(task_id) for task_id in task_ids),
                return_exceptions=True,
            )
        finally:
            await ov_client.close()

        statuses: dict[str, tuple[str, str | None]] = {}
        for task_id, task in zip(task_ids, tasks):
            if isinstance(task, BaseException):
                logger.warning("Could not refresh task %s: %s", task_id, task)
                statuses[task_id] = (INGEST_UNKNOWN, None)
                continue
            if not task:
                # Gone, not unreachable: the backend answered and has no such
                # task. Nothing further can be learned by asking again.
                statuses[task_id] = (INGEST_EXPIRED, None)
                continue
            raw = str(task.get("status") or "").lower()
            statuses[task_id] = (
                _OV_STATUS_MAP.get(raw, INGEST_UNKNOWN),
                task.get("error"),
            )
        return statuses

    async def _insert_one(
        self, ov_client: OpenVikingClient, file: ContextIngestFile, target_root: str
    ) -> IngestResult:
        """Spill one file to disk, submit it, and clean up. Never raises.

        OpenViking's ingest takes a filesystem path — it uploads the file to a
        temp endpoint — so in-memory upload bytes have to land on disk first.
        The temp directory is removed even when the submission fails.
        """
        try:
            uri = target_uri(target_root, file.relative_path)
        except ValueError as exc:
            logger.warning("Rejected ingest path %r: %s", file.relative_path, exc)
            return IngestResult(
                relative_path=file.relative_path,
                status=INGEST_FAILED,
                reason="Invalid file path.",
            )

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Mirror the full relative path, not just the basename:
                # OpenViking derives the resource's source_name from the path
                # it is handed, so a flat spill would index
                # "figure_1.png" for what the URI calls
                # "figures/figure_1.png".
                root = Path(tmp_dir).resolve()
                spill = (root / file.relative_path).resolve()
                # target_uri already rejected traversal, but this write must
                # not depend on that ordering: an absolute relative_path would
                # otherwise land outside the temp directory entirely.
                if not spill.is_relative_to(root):
                    raise ValueError(f"Unsafe relative path: {file.relative_path!r}")
                await asyncio.to_thread(
                    spill.parent.mkdir, parents=True, exist_ok=True
                )
                await asyncio.to_thread(spill.write_bytes, file.content)
                submitted = await ov_client.add_resource(
                    str(spill), uri, reason=f"BERIL user upload {file.relative_path}"
                )
        except INGEST_FAILURES as exc:
            # One bad file must not abort the batch, so expected failures are
            # recorded rather than raised — including an unreachable backend.
            logger.warning("Context ingest failed for %s: %s", uri, exc)
            return IngestResult(
                relative_path=file.relative_path,
                status=INGEST_FAILED,
                uri=uri,
                reason="The context manager rejected the file.",
            )

        return IngestResult(
            relative_path=file.relative_path,
            status=INGEST_QUEUED,
            uri=uri,
            task_id=(submitted or {}).get("task_id"),
        )

    async def glob(
        self, pattern: str, uri: str, *, node_limit: int | None = None
    ) -> list[str]:
        """URIs beneath ``uri`` matching ``pattern``, as a plain list.

        ``uri`` is resolved by the caller (see ``listing_uri``); this method
        does not scope it. A ``uri`` the backend does not know yields no
        matches rather than an error — an empty corpus is a legitimate state.

        A directory match comes back with a trailing slash; it is stripped so
        an expanded URI has the same form ``listing_uri`` produces. The
        backend reads either form identically — this is for consistency of
        what the routes hand on, not correctness.
        """
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            results = await ov_client.glob(pattern, uri, node_limit=node_limit)
        except SdkNotFoundError:
            return []
        finally:
            await ov_client.close()
        return [
            m.rstrip("/")
            for m in (results or {}).get("matches") or []
            if isinstance(m, str) and m.rstrip("/")
        ]

    async def list_files(
        self,
        uri: str | list[str],
        *,
        recursive: bool = False,
        simple: bool = False,
        node_limit: int | None = None,
    ) -> list:
        """List the resources at ``uri``, or at each of several in turn.

        ``uri`` is resolved by the caller (see ``listing_uri``) — this method
        does not scope it, so it must never be handed unvalidated caller input.
        Several URIs are listed one after another and concatenated; the backend
        lists one location at a time, so the fan-out lives here. ``node_limit``
        is one budget for the whole request, not per URI — each call gets what
        is left, and the fan-out stops once it is spent; omitted, the budget is
        the backend's own single-call default. An empty list
        is an empty listing and never reaches the backend — asking it to list
        nothing is not the same as asking it to list nowhere.

        A listing of a path the backend does not know is an empty list, not an
        error: an un-ingested project is a legitimate state, not a failure.
        """
        uris = [uri] if isinstance(uri, str) else list(uri)
        if not uris:
            return []
        budget = _Budget(node_limit, DEFAULT_LS_NODE_LIMIT, single=len(uris) == 1)
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        listed: list = []
        try:
            for one in uris:
                if budget.spent:
                    break
                try:
                    results = await ov_client.list_files(
                        one,
                        recursive=recursive,
                        simple=simple,
                        node_limit=budget.for_call(),
                    )
                except SdkNotFoundError:
                    # The backend raises for a path it does not know. Per URI,
                    # so one owner's copy vanishing between the glob and this
                    # read does not fail the others.
                    continue
                listed.extend(budget.take(list(results or [])))
        finally:
            # Closed even when the listing raises, so a failure does not leak
            # the connection.
            await ov_client.close()
        return listed

    async def find_pitfalls(
        self,
        query: str | None,
        *,
        memory_pattern: str,
        limit: int,
        exact: bool = False,
    ) -> tuple[list[dict], int, int]:
        """Search, or list, the pitfall documents.

        Returns ``(documents, fragments_scanned, total)`` — ``total`` counts
        the documents that qualified before ``limit``. See ``_find_documents``
        for the scope and the two modes.
        """
        documents, scanned = await self._find_documents(
            query, slug="pitfalls", memory_pattern=memory_pattern,
            limit=limit, exact=exact,
        )
        return documents[:limit], scanned, len(documents)

    async def find_discoveries(
        self,
        query: str | None,
        *,
        memory_pattern: str,
        limit: int,
        exact: bool = False,
    ) -> tuple[list[dict], int]:
        """Search, or list, the discovery documents — every one that qualifies.

        Untrimmed, unlike ``find_pitfalls``: the route applies the precedence
        rule first and the limit after, so a stale central duplicate cannot
        take a page slot and leave the current copy off it. Precedence lives
        above this because it needs BERIL's own record of which projects have
        a memory — a database fact the backend does not model.
        """
        return await self._find_documents(
            query, slug="discoveries", memory_pattern=memory_pattern,
            limit=limit, exact=exact,
        )

    async def _find_documents(
        self,
        query: str | None,
        *,
        slug: str,
        memory_pattern: str,
        limit: int,
        exact: bool = False,
    ) -> tuple[list[dict], int]:
        """Search, or list, one by-protocol corpus: ``slug`` is ``pitfalls``
        or ``discoveries``.

        Returns ``(documents, fragments_scanned)`` with every document that
        qualified (up to ``MAX_MEMORY_DOCUMENTS``); callers apply the limit.
        ``limit`` here only sizes the backend over-fetch.

        The scope is the corpus documents themselves, never the corpus at
        large: the central archive (``beril/docs/<slug>``) plus each project's
        memory matching ``memory_pattern`` — a glob relative to the corpus
        root, e.g. ``*/*/memories/<slug>.md``. Searching everything and
        classifying afterwards returned any file that matched — a REPORT
        fragment labelled a project memory, the performance guide labelled a
        central pitfall.

        With ``query`` omitted (``None``) nothing is searched: the documents
        in scope are returned unranked, central first. An empty string is the
        route's to reject — it is a malformed query, not a request to list.
        With a query, ``exact`` greps (it beats embeddings for the error
        strings and table names users paste) and otherwise the search is
        semantic. Hits are grouped into source documents and kept only if that
        document is one of the corpus documents — a second line of defense,
        and the only one when the scope falls back.

        Past ``MAX_MEMORY_DOCUMENTS`` memories the scope falls back to the
        narrowest directory enclosing the pattern (plus the archive), and the
        document filter does the narrowing.
        """
        central = f"{USERS_TARGET_URI}{HOUSE_ACCOUNT_ID}/docs/{slug}"
        root = corpus_root()
        memories = await self.glob(
            memory_pattern, root, node_limit=MAX_MEMORY_DOCUMENTS + 1
        )
        overflow = len(memories) > MAX_MEMORY_DOCUMENTS
        memory_set = set(memories)

        def is_corpus_document(doc_uri: str) -> bool:
            if doc_uri == central:
                return True
            if overflow:
                return _glob_match(doc_uri.removeprefix(root).strip("/"), memory_pattern)
            return doc_uri in memory_set

        if query is None:
            # A listing searches nothing. Past the cap the glob stopped early,
            # so the list is incomplete — said in the log and visible to the
            # caller as ``total`` hitting the cap.
            if overflow:
                logger.warning(
                    "%s listing stopped at %d memories", slug, MAX_MEMORY_DOCUMENTS
                )
            listed = [central, *sorted(memories)[:MAX_MEMORY_DOCUMENTS]]
            documents = [
                {"uri": uri, "score": None, "excerpts": [], "fragment_uris": []}
                for uri in listed
            ]
            return documents, 0

        if overflow:
            logger.warning(
                "%s query over %d memories; scoping to the enclosing directory",
                slug,
                len(memories),
            )
            prefix = memory_pattern.split("*", 1)[0].rstrip("/")
            enclosing = f"{root}/{prefix}" if prefix else root
            targets: list[str] = [central, enclosing] if enclosing != root else [root]
        else:
            targets = [central, *memories]

        if exact:
            nodes = _grep_nodes(
                await self.grep(targets, query, case_insensitive=True)
            )
        else:
            ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
            try:
                # Over-fetch: fragments collapse, so N nodes yield fewer
                # documents. Bounded so a broad query cannot walk the corpus.
                raw = await ov_client.find(
                    query, target_uri=targets, limit=min(limit * 5, 100)
                )
            finally:
                await ov_client.close()
            nodes = [
                {
                    "uri": r.get("uri") or "",
                    "score": float(r.get("score") or 0.0),
                    "text": r.get("abstract") or "",
                }
                for r in (raw.get("resources") or [])
            ]

        # Filtered before grouping and before any limit, so a match from some
        # other file can neither appear nor crowd a real one out of the page.
        nodes = [
            n for n in nodes
            if is_corpus_document(source_document(n.get("uri") or "", USERS_TARGET_URI))
        ]
        return _collapse_fragments(nodes, limit=MAX_MEMORY_DOCUMENTS + 1), len(nodes)

    async def grep(
        self,
        uri: str | list[str],
        pattern: str,
        *,
        case_insensitive: bool = False,
        exclude_uri: str | None = None,
        node_limit: int | None = None,
    ) -> dict:
        """Exact-pattern search beneath ``uri``, or beneath each of several.

        Both URIs are resolved by the caller (see ``listing_uri``); this method
        does not scope them, so it must never be handed unvalidated input.
        Several URIs are searched one after another and merged into one
        payload of the backend's own shape: ``matches`` concatenated,
        ``count``/``match_count`` recounted (the backend reports both, always
        equal to the number of matches), ``files_scanned`` summed.
        ``node_limit`` is one budget of matches for the whole request, spent
        across the URIs as ``list_files`` spends its own. It bounds what comes
        back, not what the backend reads: grep scans every candidate file under
        a target whatever the limit, so the scan cost of a fan-out grows with
        the number of URIs. An empty
        list is an empty result and never reaches the backend, and a path the
        backend does not know matches nothing rather than failing.

        Returns the backend's own payload shape. Unlike ``query``, there is no
        mapping layer: grep results are structural (matching nodes and their
        lines), and inventing a BERIL-side schema for them would be guesswork
        until a consumer needs one.
        """
        uris = [uri] if isinstance(uri, str) else list(uri)
        if not uris:
            return _EMPTY_GREP.copy()
        budget = _Budget(node_limit, DEFAULT_GREP_NODE_LIMIT, single=len(uris) == 1)
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            payloads = []
            for one in uris:
                if budget.spent:
                    break
                try:
                    payload = await ov_client.grep(
                        one,
                        pattern,
                        case_insensitive=case_insensitive,
                        exclude_uri=exclude_uri,
                        node_limit=budget.for_call(),
                    )
                except SdkNotFoundError:
                    # Same as list_files: an unknown path matches nothing.
                    payload = _EMPTY_GREP.copy()
                payload = payload or {}
                if not budget.single:
                    payload = {
                        **payload,
                        "matches": budget.take(list(payload.get("matches") or [])),
                    }
                payloads.append(payload)
        finally:
            await ov_client.close()
        if len(payloads) == 1:
            return payloads[0]
        matches = [m for p in payloads for m in p.get("matches") or []]
        return {
            "matches": matches,
            "count": len(matches),
            "match_count": len(matches),
            "files_scanned": sum(int(p.get("files_scanned") or 0) for p in payloads),
        }

    async def query(
        self, query: ContextQuery, *, target_uri: str | list[str]
    ) -> ContextQueryResults:
        """Search below ``target_uri``.

        The target is resolved by the caller (see ``listing_uri``) — the query
        carries addressing fields, but this method never derives a backend
        location from them. Several URIs are searched as one scope: the backend
        ranks across them, which a fan-out here could not reproduce. An empty
        list is an empty result and never reaches the backend — a missing
        target would fall back to the backend's own default scope, which is
        wider than the corpus.
        """
        if not isinstance(target_uri, str) and not target_uri:
            return ContextQueryResults(query=query.query, results=[], total=0)
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            results = await ov_client.find(
                query.query,
                target_uri=target_uri,
                limit=query.limit,
                score_threshold=query.score_threshold,
                since=query.since,
                until=query.until,
                time_field=query.time_field,
                node_limit=query.node_limit,
                read_content=query.read_content,
            )
        finally:
            # Closed even when the search raises, so a failed query does not
            # leak the connection.
            await ov_client.close()

        resources = results.get("resources") or []
        return ContextQueryResults(
            query=query.query,
            results=[
                QueryResult(
                    uri=r.get("uri") or "",
                    context_type=r.get("context_type") or "",
                    score=r.get("score") or 0.0,
                    # The abstract is a summary; `content` is the document, and
                    # only present when the caller asked to read it.
                    text=r.get("abstract") or "",
                    match_reason=r.get("match_reason"),
                    content=r.get("content"),
                )
                for r in resources
            ],
            # The backend's own count when it reports one — it can exceed the
            # number of rows returned under a limit.
            total=results.get("total") if results.get("total") is not None
            else len(resources),
        )

async def get_user_ov_api_key(db: AsyncSession, user: BerilUser) -> str:
    """
    Fetches the OpenViking api key for an authenticated user.
    If user is None or doesn't have an id, raises an UnauthenticatedError.
    If the user has no OpenViking api key, this creates the user in
    OpenViking (and locally) and returns the api key.

    Provisioning is transparent to the caller: the OpenViking account is an
    implementation detail, so a user who already exists upstream but has no key
    stored here is silently issued a fresh one rather than surfacing a conflict.
    That invalidates any prior key for that OV user — acceptable because BERIL
    is the only legitimate holder, and a key BERIL cannot read is unusable here.

    Raises OvProvisioningError if OpenViking is unreachable or returns no key.
    """
    if user is None or not getattr(user, "id", None):
        raise UnauthenticatedError(
            "An authenticated user is required to access OpenViking."
        )

    settings = get_settings()

    existing = await get_ov_credential(db, user.id)
    if existing is not None:
        return decrypt_secret(existing.encrypted_key, settings.ov_credential_key)

    # ov_user_id is always the authenticated user's ORCiD — never caller input.
    ov_user_id = user.orcid_id
    try:
        result = await register_ov_user(ov_user_id)
    except OpenVikingError as exc:
        if exc.status_code != 409 and exc.code != "ALREADY_EXISTS":
            logger.warning("OpenViking register_user failed for %s: %s", user.id, exc)
            raise OvProvisioningError(f"OpenViking user creation failed: {exc}") from exc
        # The OV user outlives BERIL's copy of its key (a dropped credential
        # row, a restored backup, a rotated encryption key). Mint a replacement
        # so the user never has to know OpenViking is involved.
        logger.info(
            "OpenViking user %s exists without a stored BERIL key; regenerating",
            ov_user_id,
        )
        try:
            result = await regenerate_ov_user_key(ov_user_id)
        except OpenVikingError as regen_exc:
            logger.warning(
                "OpenViking regenerate_key failed for %s: %s", user.id, regen_exc
            )
            raise OvProvisioningError(
                f"OpenViking key regeneration failed: {regen_exc}"
            ) from regen_exc

    user_key = (result or {}).get("user_key")
    if not user_key:
        raise OvProvisioningError(
            "OpenViking did not return a user key."
        )

    await upsert_ov_credential(
        db,
        user.id,
        account_id=settings.ov_account_id,
        ov_user_id=ov_user_id,
        encrypted_key=encrypt_secret(user_key, settings.ov_credential_key),
    )
    logger.info(
        "Stored OpenViking credential for BERIL user %s (orcid %s)",
        user.id,
        user.orcid_id,
    )
    return user_key

