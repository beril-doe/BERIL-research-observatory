import asyncio
import logging
import re
import tempfile
from pathlib import Path

import httpx
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
    INGEST_COMPLETED,
    INGEST_FAILED,
    INGEST_PROCESSING,
    INGEST_QUEUED,
    INGEST_UNKNOWN,
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

        Returns ``{task_id: (status, error)}`` in BERIL's vocabulary. A task the
        backend no longer knows maps to ``unknown`` rather than a guess — its
        record may simply have aged out.

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
                statuses[task_id] = (INGEST_UNKNOWN, None)
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

    async def list_files(
        self,
        uri: str,
        *,
        recursive: bool = False,
        simple: bool = False,
        node_limit: int | None = None,
    ) -> list:
        """List the resources at ``uri``.

        ``uri`` is resolved by the caller (see ``listing_uri``) — this method
        does not scope it, so it must never be handed unvalidated caller input.

        A listing of a path the backend does not know is an empty list, not an
        error: an un-ingested project is a legitimate state, not a failure.
        """
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            results = await ov_client.list_files(
                uri, recursive=recursive, simple=simple, node_limit=node_limit
            )
        finally:
            # Closed even when the listing raises, so a failure does not leak
            # the connection.
            await ov_client.close()
        return list(results or [])

    async def find_pitfalls(
        self,
        query: str | None,
        *,
        uri: str,
        limit: int,
        exact: bool = False,
    ) -> tuple[list[dict], int]:
        """Search the pitfall corpus, collapsed to source documents.

        Returns ``(documents, fragments_scanned)``. Semantic by default;
        ``exact`` switches to grep, which beats embeddings for error strings
        and table names — the tokens a user actually pastes in.

        Fragments are grouped by source document and synthetic nodes dropped,
        so a caller gets documents rather than section-level noise. The
        document's score is its best fragment's: a strong match anywhere in a
        pitfall entry makes that entry worth reading.
        """
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            if exact:
                raw = await ov_client.grep(uri, query or "", case_insensitive=True)
                nodes = _grep_nodes(raw)
            else:
                # Over-fetch: fragments collapse, so N nodes yield fewer
                # documents. Bounded so a broad query cannot walk the corpus.
                raw = await ov_client.find(
                    query or "", target_uri=uri, limit=min(limit * 5, 100)
                )
                nodes = [
                    {
                        "uri": r.get("uri") or "",
                        "score": float(r.get("score") or 0.0),
                        "text": r.get("abstract") or "",
                    }
                    for r in (raw.get("resources") or [])
                ]
        finally:
            await ov_client.close()

        return _collapse_fragments(nodes, limit=limit), len(nodes)

    async def grep(
        self,
        uri: str,
        pattern: str,
        *,
        case_insensitive: bool = False,
        exclude_uri: str | None = None,
        node_limit: int | None = None,
    ) -> dict:
        """Exact-pattern search beneath ``uri``.

        Both URIs are resolved by the caller (see ``listing_uri``); this method
        does not scope them, so it must never be handed unvalidated input.

        Returns the backend's own payload shape. Unlike ``query``, there is no
        mapping layer: grep results are structural (matching nodes and their
        lines), and inventing a BERIL-side schema for them would be guesswork
        until a consumer needs one.
        """
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            results = await ov_client.grep(
                uri,
                pattern,
                case_insensitive=case_insensitive,
                exclude_uri=exclude_uri,
                node_limit=node_limit,
            )
        finally:
            await ov_client.close()
        return results or {}

    async def query(self, query: ContextQuery) -> ContextQueryResults:
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        try:
            results = await ov_client.find(
                query.query,
                target_uri=query.root_path,
                limit=query.limit,
                score_threshold=query.score_threshold,
                filter=query.filter,
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

