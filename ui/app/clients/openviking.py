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

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(10.0)
# Semantic search runs an embedding + vector lookup server-side and is slower
# than the admin/provisioning calls, so it gets its own, longer budget.
_SEARCH_TIMEOUT = httpx.Timeout(30.0)


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


def _admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_settings().ov_admin_key}"}


def _user_headers(user_key: str) -> dict[str, str]:
    """Auth headers for a *data* call made as a specific OV user.

    Data endpoints (search/find) authenticate with the user's own ``user_key``
    via ``X-API-Key`` — distinct from :func:`_admin_headers`, which sends the
    account ADMIN Bearer token used only for account/user provisioning.
    """
    return {"X-API-Key": user_key}


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


async def ov_search(
    user_key: str,
    query: str,
    *,
    target_uri: str,
    limit: int,
) -> dict:
    """Run a semantic search (``find``) as the OV user holding ``user_key``.

    Returns the OV ``result`` payload — an object with ``memories``,
    ``resources``, ``skills`` lists plus ``total`` (the buckets other than the
    one matching ``target_uri`` are empty). Raises :class:`OpenVikingError` on a
    transport error or an error envelope; a rejected key surfaces as
    ``status_code`` 401/403 so callers can distinguish auth failures.
    """
    settings = get_settings()
    body = {"query": query, "target_uri": target_uri, "limit": limit+1}
    try:
        async with httpx.AsyncClient(
            base_url=settings.ov_url, timeout=_SEARCH_TIMEOUT
        ) as client:
            # Endpoint is /api/v1/search/search: the search router has prefix
            # /api/v1/search AND a /search route (/api/v1/search alone 404s).
            response = await client.post(
                "/api/v1/search/search", json=body, headers=_user_headers(user_key)
            )
    except httpx.HTTPError as exc:
        raise OpenVikingError(f"OpenViking search request failed: {exc}") from exc
    return _parse_result(response)


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
