import asyncio
import logging
import re
import tempfile
from pathlib import Path

import httpx
from openviking_sdk.errors import OpenVikingError as SdkOpenVikingError
from openviking_sdk.errors import UnauthenticatedError as SdkUnauthenticatedError
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.openviking import (
    OpenVikingClient,
    OpenVikingError,
    regenerate_ov_user_key,
    register_ov_user,
)
from app.config import Settings, get_settings
from app.crypto import CredentialEncryptionError, decrypt_secret, encrypt_secret
from app.db.crud import (
    get_ov_credential,
    upsert_ov_credential,
    users_without_ov_credential,
)
from app.db.models import BerilUser

from .base import (
    INGEST_COMPLETED,
    INGEST_EXPIRED,
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
        except SdkUnauthenticatedError:
            # Not a bad file: the credential itself was refused, so every file
            # in the batch would fail identically. Let it escape so the caller
            # can rotate the key and retry the batch, instead of recording N
            # spurious "rejected" rows for a problem that is not per-file.
            raise
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
        try:
            return decrypt_secret(existing.encrypted_key, settings.ov_credential_key)
        except CredentialEncryptionError as exc:
            # The row exists but is unreadable — the Fernet key was rotated, or
            # the ciphertext is corrupt. Functionally that is "no credential":
            # a key BERIL cannot read is unusable here. Re-provision over the
            # dead row rather than 500 on every call. (A key that is not
            # configured at all is refused at startup, so that is not this.)
            logger.warning(
                "Stored context credential for %s is unreadable (%s); re-provisioning",
                user.id,
                exc,
            )

    # ov_user_id is always the authenticated user's ORCiD — never caller input.
    try:
        result = await register_ov_user(user.orcid_id)
    except OpenVikingError as exc:
        if exc.status_code != 409 and exc.code != "ALREADY_EXISTS":
            logger.warning("OpenViking register_user failed for %s: %s", user.id, exc)
            raise OvProvisioningError(f"OpenViking user creation failed: {exc}") from exc
        # The OV user outlives BERIL's copy of its key (a dropped credential
        # row, a restored backup, a rotated encryption key). Mint a replacement
        # so the user never has to know OpenViking is involved.
        logger.info(
            "OpenViking user %s exists without a stored BERIL key; regenerating",
            user.orcid_id,
        )
        result = await _regenerate(user)

    return await _store_key(db, user, result, settings)


async def regenerate_user_ov_api_key(db: AsyncSession, user: BerilUser) -> str:
    """Mint a fresh key for ``user`` and store it, invalidating the old one.

    The repair path for a stored key the store no longer accepts — revoked out
    of band, or left stale by a provisioning race. Unlike
    :func:`get_user_ov_api_key` it never returns what is stored: the point is
    that what is stored is wrong.

    Raises :class:`UnauthenticatedError` without a persisted user, and
    :class:`OvProvisioningError` if the store will not mint a key.
    """
    if user is None or not getattr(user, "id", None):
        raise UnauthenticatedError(
            "An authenticated user is required to access OpenViking."
        )
    result = await _regenerate(user)
    return await _store_key(db, user, result, get_settings())


async def _regenerate(user: BerilUser) -> dict:
    try:
        return await regenerate_ov_user_key(user.orcid_id)
    except OpenVikingError as exc:
        logger.warning("OpenViking regenerate_key failed for %s: %s", user.id, exc)
        raise OvProvisioningError(
            f"OpenViking key regeneration failed: {exc}"
        ) from exc


async def _store_key(
    db: AsyncSession, user: BerilUser, result: dict | None, settings: Settings
) -> str:
    """Persist the key from a register/regenerate envelope; return it plain."""
    user_key = (result or {}).get("user_key")
    if not user_key:
        raise OvProvisioningError("OpenViking did not return a user key.")

    await upsert_ov_credential(
        db,
        user.id,
        account_id=settings.ov_account_id,
        ov_user_id=user.orcid_id,
        encrypted_key=encrypt_secret(user_key, settings.ov_credential_key),
    )
    logger.info(
        "Stored OpenViking credential for BERIL user %s (orcid %s)",
        user.id,
        user.orcid_id,
    )
    return user_key


class SelfHealingContextManager:
    """A manager that rotates its key and retries once when the store refuses it.

    A stored key can be dead through no fault of the current request: revoked
    out of band, or left stale by a race. Before this, such a user got a 502
    on every call forever, with nothing pointing them at the fix. Now the
    first refusal mints a replacement and the call is retried transparently.

    Retried **once**, and only on the store's own ``UnauthenticatedError`` —
    never on a 404, an outage, or a bad file. Rotating a key on those would be
    both pointless and destructive. If two workers hit a dead key together,
    both rotate and the loser's retry fails once more; the next call uses the
    stored (winning) key and succeeds. Self-correcting within one extra
    failure, so no lock is needed here.

    Proxies every attribute of the wrapped manager, so new methods inherit the
    behaviour without being listed.
    """

    def __init__(self, inner: OpenVikingManager, *, rotate) -> None:
        self._inner = inner
        self._rotate = rotate

    def __getattr__(self, name: str):
        attr = getattr(self._inner, name)
        if not callable(attr):
            return attr

        async def call(*args, **kwargs):
            try:
                return await attr(*args, **kwargs)
            except SdkUnauthenticatedError:
                logger.warning(
                    "Context store refused the stored key during %s; "
                    "rotating and retrying once",
                    name,
                )
                self._inner.api_key = await self._rotate()
                return await getattr(self._inner, name)(*args, **kwargs)

        return call


async def backfill_ov_credentials(
    db: AsyncSession, *, dry_run: bool = False
) -> tuple[list[str], list[tuple[str, str]]]:
    """Provision a credential for every user who has none.

    Returns ``(attempted, failed)`` as ORCiDs — with ``dry_run`` the worklist is
    returned as ``attempted`` and nothing is provisioned. Runs serially in one
    process, so it is race-free by construction; and it reuses
    :func:`get_user_ov_api_key`, so a user already present upstream is handled
    by the same 409-then-regenerate path as first use.
    """
    attempted: list[str] = []
    failed: list[tuple[str, str]] = []
    for user in await users_without_ov_credential(db):
        attempted.append(user.orcid_id)
        if dry_run:
            continue
        try:
            await get_user_ov_api_key(db, user)
        except (OvProvisioningError, CredentialEncryptionError) as exc:
            logger.warning("Backfill failed for %s: %s", user.orcid_id, exc)
            failed.append((user.orcid_id, str(exc)))
    return attempted, failed

