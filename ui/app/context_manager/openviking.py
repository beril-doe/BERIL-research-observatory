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
    """
    return f"{USERS_TARGET_URI}{orcid_id}/{project_slug}"


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

    async def list_files(self) -> list[ContextFile]:
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        results = await ov_client.list_files("resources/projects")
        await ov_client.close()
        return results

    async def query(self, query: ContextQuery) -> ContextQueryResults:
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        results = await ov_client.find(
            query.query,
            target_uri=query.root_path,
            limit=query.limit,
            score_threshold=query.score_threshold
        )
        processed = ContextQueryResults(
            query=query.query,
            results = [
                QueryResult(
                    uri=r.get("uri"),
                    context_type=r.get("context_type"),
                    score=r.get("score"),
                    text=r.get("abstract")
                ) for r in results.get("resources", [])
            ]
        )
        await ov_client.close()
        return processed

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

