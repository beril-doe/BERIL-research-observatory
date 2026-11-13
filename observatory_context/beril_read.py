"""Read project files and the submissions feed through BERIL's HTTP API.

Two read routes under ``/api/context/``, reached with a BERIL personal access
token and never with an OpenViking key:

  * ``GET /api/context/read?address=<owner>/<project>/<path>`` returns one
    project file, either as a JSON envelope or, with ``Accept:
    application/octet-stream``, as raw bytes with the file's sha256 in a
    header. Only a fixed allowlist of paths is readable (:data:`READABLE`).
  * ``GET /api/context/submissions?since=…&kind=…&limit=…`` lists approved
    and seeded projects in ``submitted_at`` order, with a ``next_since``
    cursor for the following page.

Both :func:`read_file` and :func:`list_submissions` take an ``httpx.Client``
that already carries the base URL and ``Authorization`` header, so the CLI
(``beril context read`` / ``submissions``) and other tooling — the wiki's
fetch adapter mirrors this contract — share one implementation.

**Byte-exactness is the contract.** Every read verifies the content's sha256
against what the server reports (the ``X-Content-SHA256`` header, or the
envelope's ``sha256``) and raises :class:`IntegrityError` on a mismatch rather
than hand back bytes that differ from what was ingested.
"""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from typing import Any, Iterable

import httpx

READ_PATH = "/api/context/read"
SUBMISSIONS_PATH = "/api/context/submissions"

# The paths a project exposes through ``read``. Mirrors the server's allowlist;
# anything else is refused with 403. Kept here so error messages can say what
# *is* readable, not just that this path is not.
READABLE = (
    "REPORT.md",
    "README.md",
    "beril.yaml",
    "CORRECTIONS.md",
    "REFUTATION_<n>.md",
    "figures/**",
)

# The feed's ``kind`` vocabulary: ``approved`` rows come from ``/submit``,
# ``seeded`` rows from an admin import.
KINDS = ("approved", "seeded")

ENCODING_UTF8 = "utf-8"
ENCODING_BASE64 = "base64"
# Marks a :class:`ContextFile` whose ``content`` is ``bytes`` (an octet-stream
# read), as opposed to the envelope's two text encodings.
ENCODING_BYTES = "bytes"


class BerilReadError(Exception):
    """A read failed. The message is user-facing; ``status`` is the HTTP status
    when the server answered, else ``None``."""

    def __init__(self, msg: str, *, status: int | None = None) -> None:
        super().__init__(msg)
        self.status = status


class IntegrityError(BerilReadError):
    """The content's sha256 does not match what the server reported for it."""


@dataclass(frozen=True)
class ContextFile:
    """One project file as BERIL returned it.

    ``content`` is ``str`` for a text file read as JSON and ``bytes`` for an
    octet-stream read (``encoding == "bytes"``) or a base64 envelope, which is
    decoded on arrival. ``sha256`` is the server's digest, already checked
    against ``content``.
    """

    address: str
    path: str
    size: int
    sha256: str
    content_type: str
    encoding: str
    content: str | bytes
    source: str
    modified_at: str | None

    @property
    def is_text(self) -> bool:
        return isinstance(self.content, str)

    def as_bytes(self) -> bytes:
        return self.content.encode("utf-8") if isinstance(self.content, str) else self.content


@dataclass(frozen=True)
class Submission:
    """One row of the submissions feed."""

    project: str
    owner_orcid: str
    address: str
    submitted_at: str
    kind: str
    batch_id: str | None
    is_public: bool
    files: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Submission":
        return cls(
            project=str(row.get("project") or ""),
            owner_orcid=str(row.get("owner_orcid") or ""),
            address=str(row.get("address") or ""),
            submitted_at=str(row.get("submitted_at") or ""),
            kind=str(row.get("kind") or ""),
            batch_id=row.get("batch_id"),
            is_public=bool(row.get("is_public", False)),
            files=list(row.get("files") or []),
        )


@dataclass(frozen=True)
class SubmissionsPage:
    """One page of the feed. ``next_since`` is the cursor to pass as ``since``
    for the following page; ``None`` when the server gave none."""

    submissions: list[Submission]
    next_since: str | None
    raw: dict[str, Any]


def read_file(client: httpx.Client, address: str, *, as_bytes: bool = False) -> ContextFile:
    """Read one project file at ``address`` (``<owner>/<project>/<path>``).

    With ``as_bytes`` the octet-stream form is used and the bytes are returned
    untouched; otherwise the JSON envelope is fetched and ``content`` is the
    file's text (or its decoded bytes when the server base64-encoded it).
    Either way the sha256 is verified; a mismatch raises :class:`IntegrityError`.

    Raises :class:`BerilReadError` with ``status`` 403 for a path outside the
    allowlist and 404 for a file that does not exist. Transport failures
    (``httpx.TransportError``) propagate for the caller to report.
    """
    headers = {"Accept": "application/octet-stream"} if as_bytes else {"Accept": "application/json"}
    response = client.get(READ_PATH, params={"address": address}, headers=headers)
    _guard(response, f"read {address}", address=address)
    return _from_bytes(response, address) if as_bytes else _from_envelope(response, address)


def list_submissions(
    client: httpx.Client,
    since: str | None = None,
    kinds: Iterable[str] | None = None,
    limit: int | None = None,
) -> SubmissionsPage:
    """One page of the submissions feed, ascending by ``submitted_at``.

    ``since`` is an ISO-8601 instant (pass a page's ``next_since`` to continue);
    ``kinds`` narrows to some of :data:`KINDS`; ``limit`` caps the page.
    """
    params: dict[str, Any] = {}
    if since:
        params["since"] = since
    if kinds is not None:
        wanted = [k.strip() for k in kinds if k and k.strip()]
        unknown = sorted(set(wanted) - set(KINDS))
        if unknown:
            raise ValueError(
                f"unknown submission kind(s) {', '.join(unknown)}; choose from {', '.join(KINDS)}"
            )
        if wanted:
            params["kind"] = ",".join(wanted)
    if limit is not None:
        if limit < 1:
            raise ValueError("--limit must be at least 1")
        params["limit"] = limit
    response = client.get(SUBMISSIONS_PATH, params=params)
    _guard(response, "list submissions")
    body = _json(response, "list submissions")
    rows = body.get("submissions")
    if not isinstance(rows, list):
        raise BerilReadError("BERIL's submissions feed had no `submissions` list.")
    next_since = body.get("next_since")
    return SubmissionsPage(
        submissions=[Submission.from_dict(r) for r in rows if isinstance(r, dict)],
        next_since=str(next_since) if next_since else None,
        raw=body,
    )


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- helpers ---------------------------------------------------------------


def _from_bytes(response: httpx.Response, address: str) -> ContextFile:
    content = response.content
    expected = response.headers.get("X-Content-SHA256", "").strip().lower()
    if not expected:
        raise IntegrityError(
            f"BERIL returned {address} without an X-Content-SHA256 header, so the "
            "bytes cannot be verified."
        )
    _verify(content, expected, address)
    return ContextFile(
        address=address,
        path=_path_of(address),
        size=len(content),
        sha256=expected,
        content_type=response.headers.get("Content-Type", "application/octet-stream"),
        encoding=ENCODING_BYTES,
        content=content,
        source=response.headers.get("X-Content-Source", ""),
        modified_at=response.headers.get("X-Content-Modified-At") or None,
    )


def _from_envelope(response: httpx.Response, address: str) -> ContextFile:
    body = _json(response, f"read {address}")
    encoding = str(body.get("encoding") or ENCODING_UTF8)
    raw = body.get("content")
    if not isinstance(raw, str):
        raise BerilReadError(f"BERIL returned {address} without a text `content` field.")
    content: str | bytes
    if encoding == ENCODING_BASE64:
        try:
            content = base64.b64decode(raw, validate=True)
        except (ValueError, TypeError) as e:
            raise BerilReadError(f"BERIL returned {address} with undecodable base64 content.") from e
    elif encoding == ENCODING_UTF8:
        content = raw
    else:
        raise BerilReadError(f"BERIL returned {address} with an unknown encoding {encoding!r}.")
    expected = str(body.get("sha256") or "").strip().lower()
    if not expected:
        raise IntegrityError(
            f"BERIL returned {address} without a sha256, so the content cannot be verified."
        )
    data = content.encode("utf-8") if isinstance(content, str) else content
    _verify(data, expected, address)
    return ContextFile(
        address=str(body.get("address") or address),
        path=str(body.get("path") or _path_of(address)),
        size=int(body.get("size") or len(data)),
        sha256=expected,
        content_type=str(body.get("content_type") or ""),
        encoding=encoding,
        content=content,
        source=str(body.get("source") or ""),
        modified_at=body.get("modified_at"),
    )


def _verify(data: bytes, expected: str, address: str) -> None:
    actual = sha256_hex(data)
    if actual != expected:
        raise IntegrityError(
            f"sha256 mismatch for {address}: BERIL reported {expected} but the "
            f"content hashes to {actual}. The bytes were not what was ingested; "
            "nothing was written."
        )


def _path_of(address: str) -> str:
    parts = [p for p in address.strip("/").split("/") if p]
    return "/".join(parts[2:])


def _guard(response: httpx.Response, action: str, *, address: str | None = None) -> None:
    if response.is_success:
        return
    status = response.status_code
    if status == 403 and address:
        raise BerilReadError(
            f"{address} is not readable through the context layer (403). Only these "
            f"project files are: {', '.join(READABLE)}.",
            status=status,
        )
    if status == 404 and address:
        raise BerilReadError(
            f"no such file: {address} (404). Check the owner, project and path with "
            "`beril context ls`.",
            status=status,
        )
    raise BerilReadError(
        f"failed to {action} (HTTP {status}): {_detail(response)}", status=status
    )


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        text = response.text.strip()
        if text[:20].lower().startswith(("<!doctype html", "<html")):
            return "the gateway returned an error page instead of BERIL's response"
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


def _json(response: httpx.Response, action: str) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError as e:
        raise BerilReadError(f"BERIL returned invalid JSON while trying to {action}.") from e
    if not isinstance(body, dict):
        raise BerilReadError(f"BERIL returned an unexpected payload while trying to {action}.")
    return body
