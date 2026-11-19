"""Record an approved submission with BERIL, so the wiki can see it.

The ``/submit`` archive step uploads a project to the lakehouse. The context
mirror (``beril_ingest``) is best-effort and indexes into OpenViking; it is not
a feed. This module writes the **submission record** that is: after the
archive succeeds, ``tools/lakehouse_upload.py`` posts one, and
``knowledge/scripts/ingest_context.py --record`` re-sends it on retry. The
server is idempotent on ``(owner, project, revision)``, where revision is the
sha256 of ``REPORT.md``.

The record must describe the archive, not the checkout: ``/submit`` edits
``beril.yaml`` and writes ``SUBMITTED.md`` after archiving, and the archive
holds a generated ``project_metadata.json`` the checkout does not. So the
upload tool archives from a staged snapshot and hashes that, and
:func:`save_pending` keeps what the record needs from it (the file list, the
approval, the archive path, ``submitted_at`` and the bytes the record sends)
under the state dir until the server reports the record complete. A retry
re-sends exactly that (:func:`load_pending`), never a rehash of the checkout.

Wire format, both with the BERIL personal access token and never an
OpenViking key:

  * ``POST /api/context/submissions`` multipart: ``manifest.json`` (project,
    owner_orcid, revision, submitted_at, archive_path, approval, and
    ``files: [{path, sha256, size}]`` for every archived file) plus
    ``bundle.zip`` holding the wiki's text files (:data:`BUNDLE_FILES`).
    Returns ``{id, status: pending|complete, missing: [paths]}``.
  * ``PUT /api/context/submissions/{id}/files/{path}`` with raw bytes, one per
    figure the REPORT embeds (:func:`embedded_figures`). Returns
    ``{status, missing}``. The server checks each body against the manifest's
    sha256 and refuses a mismatch.

Functions take an ``httpx.Client`` carrying the base URL and bearer header, as
``beril_read`` does. Transport errors propagate; HTTP failures raise
:class:`BerilSubmitError`.
"""

from __future__ import annotations

import fnmatch
import hashlib
import io
import json
import re
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import httpx

SUBMISSIONS_PATH = "/api/context/submissions"

# The text files the wiki reads, bundled with the record. Matches the
# ``read`` allowlist minus figures, which go up one PUT at a time.
BUNDLE_FILES = ("REPORT.md", "README.md", "beril.yaml", "CORRECTIONS.md", "REFUTATION_*.md")

# Where a record waits for a retry, under the state dir: one per project,
# replaced by each archive (each archive replaces the last at its path).
PENDING_DIR = "submission_records"
_PENDING_META = "record.json"
_PENDING_FILES = "files"

# Upload timeout: a figure may be tens of MiB.
UPLOAD_TIMEOUT_SECONDS = 120.0

PENDING = "pending"
COMPLETE = "complete"

# ``![alt](figures/x.png)`` and ``<img src="figures/x.png">``.
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


class BerilSubmitError(Exception):
    """A record post or file PUT failed. The message is user-facing;
    ``status`` is the HTTP status when the server answered."""

    def __init__(self, msg: str, *, status: int | None = None) -> None:
        super().__init__(msg)
        self.status = status


@dataclass(frozen=True)
class Receipt:
    """What the server said after a post or a PUT."""

    id: str
    status: str
    missing: list[str] = field(default_factory=list)

    @classmethod
    def from_body(cls, body: dict[str, Any], *, fallback_id: str = "") -> "Receipt":
        return cls(
            id=str(body.get("id") or fallback_id),
            status=str(body.get("status") or PENDING),
            missing=[str(p) for p in body.get("missing") or []],
        )


@dataclass
class RecordOutcome:
    """The result of :func:`submit_record`, in the shape ``lakehouse_upload``
    reports under ``wiki_submission``: ``status`` is ``ok`` when the server
    marked the submission complete, else ``failed`` with a ``reason``."""

    status: str
    reason: str
    id: str | None = None
    missing: list[str] = field(default_factory=list)
    revision: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "id": self.id,
            "revision": self.revision,
            "missing": list(self.missing),
        }


def client_for(base_url: str, token: str, *, timeout: float = UPLOAD_TIMEOUT_SECONDS) -> httpx.Client:
    """An httpx client for ``base_url`` carrying the BERIL bearer token — the
    shape every function here takes."""
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        timeout=timeout,
        headers={"Authorization": f"Bearer {token}"},
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_entries(root: Path, paths: Iterable[Path]) -> list[dict[str, Any]]:
    """``[{path, sha256, size}]`` for ``paths`` (absolute, under ``root``),
    sorted by relative path with forward slashes."""
    root = Path(root).resolve()
    entries = []
    for p in paths:
        p = Path(p).resolve()
        rel = p.relative_to(root).as_posix()
        entries.append({"path": rel, "sha256": sha256_file(p), "size": p.stat().st_size})
    return sorted(entries, key=lambda e: e["path"])


def is_bundle_file(rel_path: str) -> bool:
    return "/" not in rel_path and any(fnmatch.fnmatch(rel_path, pat) for pat in BUNDLE_FILES)


def embedded_figures(report_text: str) -> list[str]:
    """Project-relative paths of the images ``REPORT.md`` embeds, in order of
    first appearance. URLs and absolute paths are left out."""
    seen: list[str] = []
    for match in list(_MD_IMAGE.finditer(report_text)) + list(_HTML_IMAGE.finditer(report_text)):
        target = match.group(1).strip()
        if "://" in target or target.startswith(("/", "data:")):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if target.startswith("./"):
            target = target[2:]
        if target and target not in seen:
            seen.append(target)
    return seen


def record_paths(files: list[dict[str, Any]], report_text: str) -> list[str]:
    """The paths whose bytes the record itself sends: the bundle's text files
    and the figures ``REPORT.md`` embeds, among ``files``."""
    listed = {f["path"] for f in files}
    bundle = [p for p in sorted(listed) if is_bundle_file(p)]
    return bundle + [f for f in embedded_figures(report_text) if f in listed and f not in bundle]


@dataclass(frozen=True)
class PendingRecord:
    """A submission record kept for a retry: everything but the owner, which
    is the login's at send time. ``root`` holds the bytes it sends."""

    project: str
    archive_path: str
    submitted_at: str
    approval: dict[str, Any]
    files: list[dict[str, Any]]
    root: Path


def _pending_dir(state_dir: Path, project: str) -> Path:
    if not project or "/" in project or "\\" in project or project in {".", ".."}:
        raise ValueError(f"not a project id: {project!r}")
    return Path(state_dir) / PENDING_DIR / project


def save_pending(
    state_dir: Path,
    project: str,
    snapshot: Path,
    *,
    files: list[dict[str, Any]],
    archive_path: str,
    approval: dict[str, Any],
    submitted_at: str | None = None,
) -> PendingRecord:
    """Keep the record for ``project`` as archived from ``snapshot`` (the
    staged copy the archive was uploaded from), replacing any earlier one.
    Written aside and swapped in, so a crash leaves the old one or the new
    one, never half of either."""
    dest = _pending_dir(state_dir, project)
    staging = dest.with_name(f".{project}.tmp")
    shutil.rmtree(staging, ignore_errors=True)
    (staging / _PENDING_FILES).mkdir(parents=True)
    snapshot = Path(snapshot)
    for rel in record_paths(files, (snapshot / "REPORT.md").read_text(encoding="utf-8")):
        target = staging / _PENDING_FILES / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snapshot / rel, target)
    meta = {
        "project": project,
        "archive_path": archive_path,
        "submitted_at": submitted_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "approval": approval,
        "files": files,
    }
    (staging / _PENDING_META).write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    shutil.rmtree(dest, ignore_errors=True)
    staging.rename(dest)
    return load_pending(state_dir, project)


def load_pending(state_dir: Path, project: str) -> PendingRecord | None:
    """The record kept for ``project``, or ``None`` when there is none."""
    dest = _pending_dir(state_dir, project)
    try:
        meta = json.loads((dest / _PENDING_META).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    return PendingRecord(
        project=meta["project"],
        archive_path=meta["archive_path"],
        submitted_at=meta["submitted_at"],
        approval=meta["approval"],
        files=meta["files"],
        root=dest / _PENDING_FILES,
    )


def drop_pending(state_dir: Path, project: str) -> None:
    """Forget the kept record — the server holds it complete."""
    shutil.rmtree(_pending_dir(state_dir, project), ignore_errors=True)


def submit_pending(client: httpx.Client, pending: PendingRecord, *, owner_orcid: str) -> RecordOutcome:
    """Send a kept record (see :func:`submit_record`); on ``ok`` the caller
    may :func:`drop_pending` it."""
    return submit_record(
        client, pending.root, project=pending.project, owner_orcid=owner_orcid,
        archive_path=pending.archive_path, approval=pending.approval, files=pending.files,
        submitted_at=pending.submitted_at,
    )


def build_manifest(
    *,
    project: str,
    owner_orcid: str,
    archive_path: str,
    approval: dict[str, Any],
    files: list[dict[str, Any]],
    submitted_at: str | None = None,
) -> dict[str, Any]:
    """The ``manifest.json`` body. ``files`` must include ``REPORT.md``, whose
    sha256 is the revision."""
    by_path = {f["path"]: f for f in files}
    if "REPORT.md" not in by_path:
        raise ValueError("a submission record needs REPORT.md among its files")
    return {
        "project": project,
        "owner_orcid": owner_orcid,
        "revision": by_path["REPORT.md"]["sha256"],
        "submitted_at": submitted_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archive_path": archive_path,
        "approval": {
            "by": approval.get("by"),
            "at": approval.get("at"),
            "report_hash": _unprefixed(approval.get("report_hash")),
        },
        "files": files,
    }


def build_bundle(root: Path, files: list[dict[str, Any]]) -> tuple[bytes, list[str]]:
    """Zip the bundle files present in ``files``; return (bytes, paths)."""
    paths = [f["path"] for f in files if is_bundle_file(f["path"])]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in paths:
            archive.write(Path(root) / rel, arcname=rel)
    return buffer.getvalue(), paths


def post_record(client: httpx.Client, manifest: dict[str, Any], bundle: bytes) -> Receipt:
    """``POST /api/context/submissions``. Idempotent on (owner, project, revision)."""
    response = client.post(
        SUBMISSIONS_PATH,
        files={
            "manifest.json": ("manifest.json", json.dumps(manifest).encode("utf-8"), "application/json"),
            "bundle.zip": ("bundle.zip", bundle, "application/zip"),
        },
        timeout=UPLOAD_TIMEOUT_SECONDS,
    )
    _guard(response, f"record the submission of {manifest.get('project')}")
    return Receipt.from_body(_json(response))


def put_file(client: httpx.Client, submission_id: str, rel_path: str, data: bytes) -> Receipt:
    """``PUT /api/context/submissions/{id}/files/{path}`` with raw bytes."""
    response = client.put(
        f"{SUBMISSIONS_PATH}/{submission_id}/files/{rel_path}",
        content=data,
        headers={"Content-Type": "application/octet-stream"},
        timeout=UPLOAD_TIMEOUT_SECONDS,
    )
    _guard(response, f"upload {rel_path} to submission {submission_id}")
    return Receipt.from_body(_json(response), fallback_id=submission_id)


def submit_record(
    client: httpx.Client,
    root: Path,
    *,
    project: str,
    owner_orcid: str,
    archive_path: str,
    approval: dict[str, Any],
    files: list[dict[str, Any]],
    submitted_at: str | None = None,
) -> RecordOutcome:
    """Post the record and bundle, then PUT each figure the REPORT embeds that
    the server reports missing. Never raises for an HTTP failure: it returns a
    ``failed`` outcome, because the archive has already succeeded and the
    caller must not undo that."""
    root = Path(root)
    try:
        manifest = build_manifest(
            project=project, owner_orcid=owner_orcid, archive_path=archive_path,
            approval=approval, files=files, submitted_at=submitted_at,
        )
        bundle, _ = build_bundle(root, files)
    except (ValueError, OSError) as exc:
        return RecordOutcome("failed", f"could not build the submission record: {exc}")
    revision = manifest["revision"]
    try:
        receipt = post_record(client, manifest, bundle)
        figures = [
            f for f in embedded_figures((root / "REPORT.md").read_text(encoding="utf-8"))
            if f in {e["path"] for e in files}
        ]
        for rel in figures:
            if receipt.status == COMPLETE or rel not in receipt.missing:
                continue
            receipt = put_file(client, receipt.id, rel, (root / rel).read_bytes())
    except BerilSubmitError as exc:
        return RecordOutcome("failed", str(exc), revision=revision)
    except httpx.TransportError as exc:
        return RecordOutcome("failed", f"could not reach BERIL: {exc}", revision=revision)
    if receipt.status == COMPLETE:
        return RecordOutcome(
            "ok", f"submission {receipt.id} complete (revision {revision[:12]})",
            id=receipt.id, revision=revision,
        )
    return RecordOutcome(
        "failed",
        f"submission {receipt.id} is {receipt.status}; still missing: "
        + (", ".join(receipt.missing) or "(unspecified)"),
        id=receipt.id, missing=receipt.missing, revision=revision,
    )


# --- helpers ---------------------------------------------------------------


def _unprefixed(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text.split(":", 1)[1] if text.startswith("sha256:") else text


def _guard(response: httpx.Response, action: str) -> None:
    if response.is_success:
        return
    detail = ""
    try:
        body = response.json()
        if isinstance(body, dict) and body.get("detail"):
            detail = f": {body['detail']}"
    except ValueError:
        text = response.text.strip()
        detail = f": {text[:200]}" if text else ""
    raise BerilSubmitError(
        f"BERIL returned {response.status_code} on {action}{detail}", status=response.status_code
    )


def _json(response: httpx.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError as exc:
        raise BerilSubmitError("BERIL returned invalid JSON for the submission call.") from exc
    if not isinstance(body, dict):
        raise BerilSubmitError("BERIL returned an unexpected submission payload.")
    return body
