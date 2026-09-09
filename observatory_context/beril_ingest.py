"""Mirror a project into the context layer through BERIL's HTTP API.

This is the ``/submit`` path. It deliberately does **not** speak OpenViking:
BERIL brokers the context manager behind ``/api/context/*``, so the CLI holds
only a BERIL personal access token and never an OV key. OpenViking's address,
credentials, and task vocabulary stay on the server side.

The wire format is the one ``POST /api/context/ingest_files`` expects:

  * a zip archive carrying the staged project's directory structure, and
  * a manifest naming which of its members to ingest, one relative path per
    line.

A plain multipart upload would flatten ``memories/pitfalls.md`` to
``pitfalls.md``; the archive is what preserves the path. Ingest is asynchronous,
so submission returns a ``batch_id`` that :func:`poll_batch` follows to a
terminal state.
"""

from __future__ import annotations

import io
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# The context routes are slower than the credential exchange in
# `beril_cli.ov_client` — an ingest upload carries a whole project archive.
UPLOAD_TIMEOUT_SECONDS = 120.0
POLL_TIMEOUT_SECONDS = 30.0

# Poll cadence and ceiling. Ingest is queue-backed, so the wait is dominated by
# the backend's own indexing, not by us asking too slowly.
POLL_INTERVAL_SECONDS = 3.0
POLL_MAX_WAIT_SECONDS = 600.0

INGEST_PATH = "/api/context/ingest_files"
STATUS_PATH = "/api/context/ingest_status"

# BERIL's ingest vocabulary (see ui/app/context_manager/base.py). Mirrored here
# rather than imported: the CLI does not depend on the webapp package.
QUEUED = "queued"
PROCESSING = "processing"
COMPLETED = "completed"
FAILED = "failed"
UNKNOWN = "unknown"

TERMINAL_STATUSES = frozenset({COMPLETED, FAILED})


class BerilIngestError(Exception):
    """An ingest submission or poll failed. The message is user-facing."""


@dataclass
class IngestOutcome:
    """The result of one mirror attempt.

    ``ok`` is true only when every manifest file reached ``completed``. A batch
    that timed out is not a failure of the upload — the files may still land —
    so it is reported separately via ``timed_out`` and the caller decides how
    loudly to say so.
    """

    ok: bool
    batch_id: str | None
    status: str
    counts: dict[str, int] = field(default_factory=dict)
    failures: list[tuple[str, str | None]] = field(default_factory=list)
    timed_out: bool = False

    def summary(self) -> str:
        """One line describing the outcome, suitable for a verdict ``reason``."""
        if self.ok:
            n = self.counts.get(COMPLETED, 0)
            return f"{n} file(s) ingested"
        if self.timed_out:
            pending = self.counts.get(QUEUED, 0) + self.counts.get(PROCESSING, 0)
            return (
                f"timed out after {POLL_MAX_WAIT_SECONDS:.0f}s with {pending} "
                f"file(s) still in flight (batch {self.batch_id})"
            )
        if self.failures:
            detail = "; ".join(
                f"{path}: {reason or 'no reason given'}"
                for path, reason in self.failures[:5]
            )
            more = "" if len(self.failures) <= 5 else f" (+{len(self.failures) - 5} more)"
            return f"{len(self.failures)} file(s) failed — {detail}{more}"
        return f"ingest ended in status {self.status!r}"


def build_archive(root: Path, files: list[Path]) -> tuple[bytes, list[str]]:
    """Zip ``files`` relative to ``root``; return ``(archive_bytes, manifest)``.

    The manifest is every archived path, in the order given, so the caller can
    hand both halves to :func:`submit_ingest` unchanged. Paths are stored
    POSIX-style because the server splits on ``/``.
    """
    root = Path(root).resolve()
    manifest: list[str] = []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            resolved = Path(path).resolve()
            if not resolved.is_file():
                raise BerilIngestError(f"Not a file: {path}")
            try:
                relative = resolved.relative_to(root)
            except ValueError as exc:
                raise BerilIngestError(
                    f"{path} is outside the staged project root {root}"
                ) from exc
            arcname = relative.as_posix()
            zf.write(resolved, arcname)
            manifest.append(arcname)

    if not manifest:
        raise BerilIngestError(f"No files to ingest under {root}")
    return buf.getvalue(), manifest


def submit_ingest(
    base_url: str,
    token: str,
    *,
    project: str,
    archive: bytes,
    manifest: list[str],
    client: httpx.Client | None = None,
) -> dict:
    """POST one archive + manifest. Returns the decoded ingest response.

    Raises :class:`BerilIngestError` on transport failure or a non-2xx — a
    rejected upload is a real failure here, unlike the gates in the caller,
    because the archive was accepted for transmission and then refused.
    """
    files = {
        "archive": (f"{project}.zip", archive, "application/zip"),
        "manifest": ("manifest.txt", "\n".join(manifest).encode(), "text/plain"),
    }
    with _client_ctx(client, UPLOAD_TIMEOUT_SECONDS) as http:
        try:
            resp = http.post(
                _url(base_url, INGEST_PATH),
                data={"project": project},
                files=files,
                headers=_auth(token),
            )
        except httpx.HTTPError as exc:
            raise BerilIngestError(f"could not reach BERIL to ingest: {exc}") from exc
        _guard(resp, "submit files for ingest")
        return _json(resp)


def poll_batch(
    base_url: str,
    token: str,
    batch_id: str,
    *,
    interval: float = POLL_INTERVAL_SECONDS,
    max_wait: float = POLL_MAX_WAIT_SECONDS,
    client: httpx.Client | None = None,
    sleep=time.sleep,
    monotonic=time.monotonic,
) -> IngestOutcome:
    """Poll a batch until every file is terminal, or ``max_wait`` elapses.

    The batch rolls up to ``failed`` as soon as any one file fails, so polling
    stops there rather than waiting out the rest — the mirror is already not
    clean. A transport blip mid-poll is retried rather than raised: the files
    are queued server-side regardless of whether we can currently see them.
    """
    deadline = monotonic() + max_wait
    last: dict = {}
    with _client_ctx(client, POLL_TIMEOUT_SECONDS) as http:
        while True:
            try:
                resp = http.get(
                    _url(base_url, f"{STATUS_PATH}/{batch_id}"), headers=_auth(token)
                )
                _guard(resp, "check ingest status")
                last = _json(resp)
            except BerilIngestError:
                # Keep the last good reading and try again; only a timeout ends
                # the loop. A 404 would be permanent, but the batch id came
                # from a 200 submission, so treating it as transient is safe.
                last = last or {}
            else:
                status = str(last.get("status") or UNKNOWN)
                if status in TERMINAL_STATUSES:
                    return _outcome(batch_id, last, timed_out=False)

            if monotonic() >= deadline:
                return _outcome(batch_id, last, timed_out=True)
            sleep(min(interval, max(0.0, deadline - monotonic())))


def _outcome(batch_id: str, body: dict, *, timed_out: bool) -> IngestOutcome:
    status = str(body.get("status") or UNKNOWN)
    counts = body.get("counts") or {}
    files = body.get("files") or []
    failures = [
        (str(f.get("relative_path") or "?"), f.get("error"))
        for f in files
        if f.get("status") == FAILED
    ]
    return IngestOutcome(
        ok=(not timed_out and status == COMPLETED and not failures),
        batch_id=batch_id,
        status=status,
        counts={str(k): int(v) for k, v in counts.items()},
        failures=failures,
        timed_out=timed_out,
    )


def ingest_project_files(
    base_url: str,
    token: str,
    *,
    project: str,
    root: Path,
    files: list[Path],
    client: httpx.Client | None = None,
    **poll_kwargs,
) -> IngestOutcome:
    """Archive, submit, and poll to a terminal state. The whole mirror."""
    archive, manifest = build_archive(root, files)
    body = submit_ingest(
        base_url,
        token,
        project=project,
        archive=archive,
        manifest=manifest,
        client=client,
    )
    batch_id = body.get("batch_id")
    if not batch_id:
        # Without a batch id the submission cannot be followed. Report what the
        # server said about the files it did accept rather than claiming success.
        raise BerilIngestError(
            "BERIL accepted the upload but returned no batch_id to poll "
            f"(queued={body.get('queued')}, failed={body.get('failed')})"
        )
    return poll_batch(base_url, token, str(batch_id), client=client, **poll_kwargs)


# --- helpers ---------------------------------------------------------------


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


class _Borrowed:
    """Use a caller-supplied client without closing it on exit."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def __enter__(self) -> httpx.Client:
        return self._client

    def __exit__(self, *exc) -> bool:
        return False


def _client_ctx(client: httpx.Client | None, timeout: float):
    """Borrow the caller's client, or open one for the duration of the call.

    The auth header is attached per-request rather than to the client, so a
    borrowed client is authenticated the same way an owned one is.
    """
    if client is not None:
        return _Borrowed(client)
    return httpx.Client(timeout=timeout)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _guard(resp: httpx.Response, action: str) -> None:
    if resp.is_success:
        return
    detail = ""
    try:
        body = resp.json()
        if isinstance(body, dict) and body.get("detail"):
            detail = f": {body['detail']}"
    except ValueError:
        text = resp.text.strip()
        detail = f": {text[:200]}" if text else ""
    raise BerilIngestError(f"BERIL returned {resp.status_code} on {action}{detail}")


def _json(resp: httpx.Response) -> dict:
    try:
        body = resp.json()
    except ValueError as exc:
        raise BerilIngestError("BERIL returned invalid JSON for the ingest call.") from exc
    if not isinstance(body, dict):
        raise BerilIngestError("BERIL returned an unexpected ingest payload.")
    return body
