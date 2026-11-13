"""Record an approved submission with BERIL, so the wiki can see it.

The ``/submit`` archive step uploads a project to the lakehouse. The context
mirror (``beril_ingest``) is best-effort and indexes into OpenViking; it is not
a feed. This module writes the **submission record** that is: after the
archive succeeds, ``tools/lakehouse_upload.py`` posts one, and
``knowledge/scripts/ingest_context.py --record`` re-sends it on retry. The
server is idempotent on ``(owner, project, revision)``, where revision is the
sha256 of ``REPORT.md``.

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

# Names the lakehouse archive leaves out (tools/lakehouse_upload.py's
# SKIP_PATTERNS, mirrored so a retried record lists the same files).
ARCHIVE_SKIP = frozenset({
    "__pycache__", ".ipynb_checkpoints", ".DS_Store", "Thumbs.db",
    ".submit.lock", "project_metadata.json",
})

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


def project_files(root: Path, skip: Iterable[str] = ARCHIVE_SKIP) -> list[Path]:
    """Every file under ``root``, leaving out names in ``skip`` (directories or
    files). The retry path's stand-in for the archive's own file list; the
    generated ``project_metadata.json`` is archived but not on disk, so a
    retried record lists one file fewer than the original."""
    skip = set(skip)
    out = []
    for p in sorted(Path(root).rglob("*")):
        if any(part in skip for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            out.append(p)
    return out


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
