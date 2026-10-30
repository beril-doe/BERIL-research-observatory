"""Query BERIL's context layer over HTTP with the stored BERIL login.

Wraps the read routes under ``/api/context/`` — ``find``, ``ls``, ``grep``,
``pitfalls``, ``discoveries`` and ``health`` — plus ``/api/user/whoami``, with
the personal access token from ``beril login``. Nothing here knows how BERIL stores the content: results
name resources by **address** (``<owner>/<project>/<path>``), the same three
parts every read takes, so any address a result returns can be fed back in.

Uses httpx (already a beril-cli dependency) for the same Cloudflare-UA reason
documented in ``auth_cmd``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

_HTTP_TIMEOUT_SECONDS = 60.0


class ContextError(Exception):
    """A context request failed. The message is user-facing.

    ``auth_failed`` marks a rejected token (HTTP 401), which the caller should
    answer with ``beril login`` rather than a retry.
    """

    def __init__(self, msg: str, *, auth_failed: bool = False) -> None:
        super().__init__(msg)
        self.auth_failed = auth_failed


@dataclass(frozen=True)
class Scope:
    """Where a read looks, in the routes' own terms.

    ``project`` alone means the caller's own project, ``owner`` narrows to one
    person, ``all_owners`` spans everyone; ``path`` is below the project. The
    server applies those rules — this only carries the fields.
    """

    project: str | None = None
    owner: str | None = None
    path: str | None = None
    all_owners: bool = False

    @classmethod
    def from_address(cls, address: str) -> "Scope":
        """Split an address (``owner/project/path``) into a scope."""
        parts = [p for p in address.strip("/").split("/") if p]
        if not parts:
            raise ValueError("an address needs at least an owner")
        return cls(
            owner=parts[0],
            project=parts[1] if len(parts) > 1 else None,
            path="/".join(parts[2:]) or None,
        )

    def params(self, prefix: str = "") -> dict[str, Any]:
        """Query parameters for this scope; ``prefix`` names an exclusion.

        An exclusion is one place, so it cannot be ``all_owners`` — the route
        has no such field, and dropping it quietly would exclude nothing."""
        if prefix and self.all_owners:
            raise ValueError("an exclusion names one owner's project, not every owner's")
        out: dict[str, Any] = {}
        if self.project is not None:
            out[f"{prefix}project"] = self.project
        if self.owner is not None:
            out[f"{prefix}owner"] = self.owner
        if self.path is not None:
            out[f"{prefix}path"] = self.path
        if self.all_owners:
            out[f"all_{prefix}owners"] = True
        return out


class ContextClient:
    """One BERIL server and token. Use as a context manager, or ``close()``."""

    def __init__(self, base_url: str, token: str, *, timeout: float = _HTTP_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}"},
        )

    def __enter__(self) -> "ContextClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def find(self, query: str, scope: Scope = Scope(), **options: Any) -> dict:
        """Semantic search. ``options`` are the route's other fields
        (``limit``, ``score_threshold``, ``since``, ``until``, ``time_field``,
        ``node_limit``, ``read_content``); ``None`` values are left out."""
        body = {"query": query, **scope.params(), **_present(options)}
        return self._call("POST", "/api/context/find", "search", json=body)

    def ls(self, scope: Scope = Scope(), **options: Any) -> list:
        """List a scope. ``options``: ``recursive``, ``simple``, ``node_limit``,
        ``depth`` (with ``recursive``)."""
        params = {**scope.params(), **_present(options)}
        return self._call("GET", "/api/context/ls", "list", params=params)

    def grep(
        self,
        pattern: str,
        scope: Scope = Scope(),
        *,
        exclude: Scope | None = None,
        **options: Any,
    ) -> dict:
        """Exact-pattern search. ``options``: ``case_insensitive``,
        ``node_limit``. ``exclude`` names a scope to leave out."""
        params = {
            "pattern": pattern,
            **scope.params(),
            **(exclude.params("exclude_") if exclude else {}),
            **_present(options),
        }
        return self._call("GET", "/api/context/grep", "search", params=params)

    def pitfalls(self, query: str | None = None, **options: Any) -> dict:
        """Pitfall documents matching ``query``, or all of them when omitted.
        ``options``: ``project``, ``owner``, ``exact``, ``limit``."""
        params = _present({"q": query, **options})
        return self._call("GET", "/api/context/pitfalls", "search pitfalls", params=params)

    def discoveries(self, query: str | None = None, **options: Any) -> dict:
        """Discovery documents, as ``pitfalls``."""
        params = _present({"q": query, **options})
        return self._call(
            "GET", "/api/context/discoveries", "search discoveries", params=params
        )

    def whoami(self) -> dict:
        """Who BERIL says the token belongs to (``orcid_id``, ``display_name``)."""
        return self._call("GET", "/api/user/whoami", "identify you")

    def health(self) -> dict:
        """``{"status": "ok"|"unavailable"}``. Answering at all also proves
        BERIL is reachable and the token is good."""
        return self._call("GET", "/api/context/health", "check context health")

    def _call(self, method: str, path: str, action: str, **kwargs: Any) -> Any:
        url = self.base_url + path
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as e:
            raise ContextError(f"timed out talking to {url}.") from e
        except httpx.TransportError as e:
            raise ContextError(f"could not reach {url}: {e}") from e
        if response.status_code == 401:
            raise ContextError(
                f"your BERIL token was rejected (401) while trying to {action}. "
                "Run `beril login` to log in again.",
                auth_failed=True,
            )
        if not response.is_success:
            raise ContextError(
                f"failed to {action} (HTTP {response.status_code}): {_detail(response)}"
            )
        try:
            return response.json()
        except ValueError as e:
            raise ContextError(f"BERIL returned invalid JSON while trying to {action}.") from e


def _present(options: dict[str, Any]) -> dict[str, Any]:
    """Drop unset options, so the route's own defaults apply."""
    return {k: v for k, v in options.items() if v is not None and v is not False}


def _detail(response: httpx.Response) -> str:
    """Best-effort human-readable reason from a failed response body.

    FastAPI's validation errors (422) carry a list of problems; each is
    reduced to its field and message.
    """
    try:
        body = response.json()
    except ValueError:
        text = response.text.strip()
        if text[:20].lower().startswith(("<!doctype html", "<html")):
            # A gateway's error page (Cloudflare, ingress), not BERIL's answer:
            # its markup tells the user nothing, and it can stand in for an
            # error BERIL did report.
            return (
                "the gateway returned an error page instead of BERIL's response "
                f"(HTTP {response.status_code}); if it persists, run "
                "`beril context doctor` or tell a BERIL admin"
            )
        return text[:200] or "no detail"
    detail = body.get("detail") if isinstance(body, dict) else None
    if isinstance(detail, list):
        parts = []
        for item in detail:
            if isinstance(item, dict):
                field = ".".join(str(x) for x in item.get("loc", [])[1:])
                parts.append(f"{field}: {item.get('msg')}" if field else str(item.get("msg")))
        return "; ".join(parts) or "invalid request"
    return str(detail) if detail else "no detail"
