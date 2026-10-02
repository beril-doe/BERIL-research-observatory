"""Async HTTP client for a deployed OpenViking (OV) instance.

BERIL authenticates as the ``beril_admin`` ADMIN of the pre-existing
``settings.ov_account_id`` account, using ``settings.ov_admin_key`` as a Bearer
token. All admin calls are scoped to that single account.

OpenViking responses use a ``{status, result, error}`` envelope. On a non-2xx
status the body carries ``error: {code, message}``; we raise
:class:`OpenVikingError` with the HTTP status and that error code so callers can
distinguish cases like ``409 / ALREADY_EXISTS``.

The OV ``user_key`` (the credential we hand back to users) is returned in
plaintext only at user creation and key regeneration — never logged here.
"""

import asyncio
import logging

import httpx
from openviking_sdk import AsyncHTTPClient
from openviking_sdk.errors import (
    DeadlineExceededError,
    EmbeddingFailedError,
    InternalError,
    ProcessingError,
    ResourceExhaustedError,
    UnavailableError,
    VLMFailedError,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(10.0)

# Errors that usually clear on a retry — OV's temp tier collides under
# back-to-back uploads. Same set the batch CLI ingest retries on.
TRANSIENT_OV_ERRORS: tuple[type[Exception], ...] = (
    DeadlineExceededError,
    EmbeddingFailedError,
    InternalError,
    ProcessingError,
    ResourceExhaustedError,
    UnavailableError,
    VLMFailedError,
)

# Deliberately tighter than the CLI's 3 attempts / 5s linear backoff: this runs
# inside a request, so the whole retry budget has to stay well under a
# request timeout. Submissions use wait=False, so an attempt is just a queue
# handoff — a retry here is cheap.
ADD_RESOURCE_RETRIES = 2
ADD_RESOURCE_BACKOFF_SECONDS = 1.0


class OpenVikingError(RuntimeError):
    """An OpenViking request failed (transport error or error envelope)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class OpenVikingClient:
    def __init__(self, api_key: str, base_url: str | None = None):
        settings = get_settings()
        self._api_key = api_key
        self._base_url = base_url or settings.ov_url
        self._client: AsyncHTTPClient = AsyncHTTPClient(
            url=self._base_url,
            api_key=self._api_key
        )

    @classmethod
    async def create(cls, api_key: str, base_url: str | None = None):
        client = cls(api_key, base_url=base_url)
        await client._client.initialize()
        return client

    async def close(self):
        await self._client.close()

    async def find(
        self,
        query: str,
        target_uri: str | None = None,
        limit: int = 10,
        score_threshold: float | None = None,
        *,
        filter: dict | None = None,
        since: str | None = None,
        until: str | None = None,
        time_field: str | None = None,
        node_limit: int | None = None,
        read_content: bool = False,
    ) -> dict:
        """Semantic search.

        Options are built by omission: a key absent from the dict lets the
        backend apply its own default, which is not the same as passing None.
        The time bounds are handed over as given — the backend owns that
        grammar, so translating it here would only add a second thing to keep
        in sync.
        """
        options = {
            key: value
            for key, value in (
                ("score_threshold", score_threshold),
                ("filter", filter),
                ("since", since),
                ("until", until),
                ("time_field", time_field),
                ("node_limit", node_limit),
                # Sent only when asked: the default is the backend's, and
                # False is a meaningful value we must not imply.
                ("read_content", read_content or None),
            )
            if value is not None
        }
        return await self._client.find(
            query,
            limit=limit,
            target_uri=target_uri,
            options=options or None,
        )

    async def list_files(self, root_path: str) -> dict:
        result = await self._client.ls(f"viking://{root_path}")
        return result

    async def get_task(self, task_id: str) -> dict | None:
        """Fetch an async task record, or None if the backend no longer has it.

        OpenViking expires task records (24h completed / 7d failed), so None
        means "expired or never existed" — it is not proof of failure.
        """
        return await self._client.get_task(task_id)

    async def add_resource(self, path: str, target_uri: str, *, reason: str) -> dict:
        """Submit a file on disk for ingestion at ``target_uri``.

        ``wait=False`` returns as soon as OpenViking queues the work — indexing
        finishes asynchronously. Callers must not block on completion inside a
        request; draining the queue can take minutes.

        Retries transient errors with linear backoff. Any other error, and the
        final transient one, propagate to the caller.
        """
        for attempt in range(1, ADD_RESOURCE_RETRIES + 1):
            try:
                return await self._client.add_resource(
                    path=path, to=target_uri, wait=False, options={"reason": reason}
                )
            except TRANSIENT_OV_ERRORS:
                if attempt == ADD_RESOURCE_RETRIES:
                    raise
                logger.info(
                    f"Transient OpenViking error adding {target_uri} ",
                    f"(attempt {attempt}/{ADD_RESOURCE_RETRIES}); retrying"
                )
                await asyncio.sleep(ADD_RESOURCE_BACKOFF_SECONDS * attempt)


def _admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_settings().ov_admin_key}"}


def _parse_result(response: httpx.Response) -> dict:
    """Validate an OV response and return its ``result`` payload.

    Raises :class:`OpenVikingError` on non-2xx status or an error envelope,
    carrying the OV error code and message (never the request/auth headers).
    """
    try:
        body = response.json()
    except ValueError:
        body = None

    if response.is_success and isinstance(body, dict) and body.get("status") == "ok":
        return body.get("result")

    code = None
    message = f"OpenViking returned HTTP {response.status_code}"
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        err = body["error"]
        code = err.get("code")
        message = err.get("message") or message
    raise OpenVikingError(message, status_code=response.status_code, code=code)


async def ov_health() -> dict:
    """Hit the public ``GET /health`` endpoint (no auth). Returns the body."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(base_url=settings.ov_url, timeout=_TIMEOUT) as client:
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise OpenVikingError(f"OpenViking health check failed: {exc}") from exc


async def register_ov_user(ov_user_id: str, role: str = "user") -> dict:
    """Register ``ov_user_id`` in the BERIL account. Returns the result payload.

    The result includes ``user_key`` (plaintext) when the OV server is not in
    key-hashing mode. Raises ``OpenVikingError`` with code ``ALREADY_EXISTS``
    (status 409) if the user already exists.
    """
    settings = get_settings()
    url = f"/api/v1/admin/accounts/{settings.ov_account_id}/users"
    try:
        async with httpx.AsyncClient(base_url=settings.ov_url, timeout=_TIMEOUT) as client:
            response = await client.post(
                url, json={"user_id": ov_user_id, "role": role}, headers=_admin_headers()
            )
    except httpx.HTTPError as exc:
        raise OpenVikingError(f"OpenViking register_user request failed: {exc}") from exc
    return _parse_result(response)


async def regenerate_ov_user_key(ov_user_id: str) -> dict:
    """Regenerate ``ov_user_id``'s API key. Returns the result (incl. ``user_key``).

    This immediately invalidates the user's previous key.
    """
    settings = get_settings()
    url = f"/api/v1/admin/accounts/{settings.ov_account_id}/users/{ov_user_id}/key"
    try:
        async with httpx.AsyncClient(base_url=settings.ov_url, timeout=_TIMEOUT) as client:
            response = await client.post(url, headers=_admin_headers())
    except httpx.HTTPError as exc:
        raise OpenVikingError(f"OpenViking regenerate_key request failed: {exc}") from exc
    return _parse_result(response)


async def ov_user_exists(ov_user_id: str) -> bool:
    """Return True if ``ov_user_id`` exists in the BERIL account.

    Informational only — not used to gate creation (avoids a TOCTOU race).
    """
    settings = get_settings()
    url = f"/api/v1/admin/accounts/{settings.ov_account_id}/users"
    try:
        async with httpx.AsyncClient(base_url=settings.ov_url, timeout=_TIMEOUT) as client:
            response = await client.get(
                url, params={"name": ov_user_id}, headers=_admin_headers()
            )
    except httpx.HTTPError as exc:
        raise OpenVikingError(f"OpenViking list_users request failed: {exc}") from exc
    users = _parse_result(response) or []
    return any(u.get("user_id") == ov_user_id for u in users)
