"""Fetch a user's OpenViking (OV) credential from BERIL with a Bearer PAT.

BERIL brokers OV credentials: an authenticated user POSTs ``/api/ov/user`` to
provision their OV account (idempotent) and GETs ``/api/ov/credentials`` to read
back the OV url + user_key. This module wraps that two-step exchange using the
stored personal access token, so ``beril login`` and ``beril ov`` share one
implementation instead of each re-deriving the endpoint/error handling.

Auth is ``Authorization: Bearer <token>`` — the same header ``_whoami`` uses.
This is the headless replacement for the browser-cookie flow in
``knowledge/scripts/setup_remote_ov.py``.

Uses httpx (already a beril-cli dependency) for the same Cloudflare-UA reason
documented in ``auth_cmd``.
"""

from __future__ import annotations

import httpx

_USER_PATH = "/api/ov/user"
_REGENERATE_PATH = "/api/ov/user/regenerate"
_CREDENTIALS_PATH = "/api/ov/credentials"
_HEALTH_PATH = "/api/ov/health"
_HTTP_TIMEOUT_SECONDS = 15.0


class OvLinkError(Exception):
    """An OpenViking credential exchange failed. Message is user-facing.

    ``needs_regenerate`` marks the specific recoverable case where OpenViking
    already has a user for this ORCiD but BERIL holds no key for it (HTTP 409
    from ``POST /api/ov/user``) — the caller should point the user at
    ``beril ov setup --regenerate``.
    """

    def __init__(self, msg: str, *, needs_regenerate: bool = False) -> None:
        super().__init__(msg)
        self.needs_regenerate = needs_regenerate


def fetch_ov_credential(
    base_url: str, token: str, *, regenerate: bool = False
) -> tuple[str, str]:
    """Provision (or rotate) and return ``(ov_url, ov_user_key)``.

    With ``regenerate=False`` (default), POSTs ``/api/ov/user`` — idempotent, so
    a user who already has a stored key just gets it back. With
    ``regenerate=True``, POSTs ``/api/ov/user/regenerate`` to mint a fresh key
    (invalidating the old one) — the recovery path for the 409 case and for key
    rotation. Either way, the key is then read via ``GET /api/ov/credentials``.

    The returned ``ov_url`` is always ``{base_url}/ov`` — the public proxy path
    the client already reached BERIL on. We deliberately ignore the ``ov_url``
    in BERIL's response: that field is ``settings.ov_url``, the address BERIL
    uses to reach OpenViking *server-to-server* (e.g. ``http://openviking:1933``
    inside a compose/SPIN network), which is not resolvable from the client.

    Raises :class:`OvLinkError` on any failure, with a message suitable for
    printing to the user.
    """
    base = base_url.rstrip("/")
    ov_url = f"{base}/ov"
    with httpx.Client(
        timeout=_HTTP_TIMEOUT_SECONDS,
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        if regenerate:
            resp = _request(client, "POST", base + _REGENERATE_PATH)
            _guard(resp, action="regenerate your OpenViking key")
        else:
            resp = _request(client, "POST", base + _USER_PATH)
            if resp.status_code == 409:
                raise OvLinkError(
                    "OpenViking already has a user for your ORCiD, but BERIL "
                    "holds no key for it.",
                    needs_regenerate=True,
                )
            _guard(resp, action="create your OpenViking account")

        creds = _request(client, "GET", base + _CREDENTIALS_PATH)
        _guard(creds, action="fetch your OpenViking credentials")

    try:
        body = creds.json()
    except ValueError as e:
        raise OvLinkError("BERIL returned invalid JSON for OpenViking credentials.") from e

    # Only the key comes from the response; the URL is the proxy path derived
    # from base_url above (BERIL's response ov_url is its internal address).
    user_key = (body or {}).get("user_key")
    if not user_key:
        raise OvLinkError(
            "BERIL did not return an OpenViking user_key."
        )
    return (ov_url, user_key)


def ov_health(base_url: str, token: str) -> dict:
    """Return BERIL's view of OpenViking health via ``GET /api/ov/health``.

    The route always answers 200 with ``{"status": "ok"|"unreachable", ...}``
    when the caller is authenticated. Raises :class:`OvLinkError` on transport
    failure or a non-2xx (e.g. 401).
    """
    base = base_url.rstrip("/")
    with httpx.Client(
        timeout=_HTTP_TIMEOUT_SECONDS,
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        resp = _request(client, "GET", base + _HEALTH_PATH)
        _guard(resp, action="check OpenViking health")
    try:
        return resp.json()
    except ValueError as e:
        raise OvLinkError("BERIL returned invalid JSON for OpenViking health.") from e


def _request(client: httpx.Client, method: str, url: str) -> httpx.Response:
    try:
        return client.request(method, url)
    except httpx.TimeoutException as e:
        raise OvLinkError(f"timed out talking to {url}.") from e
    except httpx.TransportError as e:
        raise OvLinkError(f"could not reach {url}: {e}") from e


def _guard(response: httpx.Response, *, action: str) -> None:
    """Raise :class:`OvLinkError` unless the response is a success."""
    if response.is_success:
        return
    if response.status_code == 401:
        raise OvLinkError(
            f"your token was rejected (401) while trying to {action}."
        )
    raise OvLinkError(f"failed to {action}: {_detail(response)}")


def _detail(response: httpx.Response) -> str:
    """Best-effort human-readable reason from a failed response body."""
    try:
        body = response.json()
    except ValueError:
        return response.text.strip()[:200] or f"HTTP {response.status_code}"
    if isinstance(body, dict) and body.get("detail"):
        return str(body["detail"])
    return f"HTTP {response.status_code}"
