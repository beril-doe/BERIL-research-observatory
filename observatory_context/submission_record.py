"""The submission record as kept on disk for a retry. Standard library only.

``tools/lakehouse_upload.py`` keeps the record here before it sends anything,
and must be able to even on an interpreter without the beril-cli dependencies
(``httpx``, ``yaml``): that is exactly when the send is skipped and the retry
(``knowledge/scripts/ingest_context.py --record``, run in the project
environment) needs what was kept. Sending lives in
:mod:`observatory_context.beril_submit`, which re-exports these names.
"""

from __future__ import annotations

import fnmatch
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# The text files the wiki reads, bundled with the record — the ``read``
# allowlist minus figures, which go up one PUT at a time — plus REVIEW.md:
# BERIL checks the approval's review_hash against its bytes, keeps it with
# the record, and never serves it.
BUNDLE_FILES = ("REPORT.md", "README.md", "beril.yaml", "REVIEW.md", "CORRECTIONS.md", "REFUTATION_*.md")

# Where a record waits for a retry, under the state dir: one per project,
# replaced by each archive (each archive replaces the last at its path).
PENDING_DIR = "submission_records"
_PENDING_META = "record.json"
_PENDING_FILES = "files"

# ``![alt](figures/x.png)`` and ``<img src="figures/x.png">``.
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


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
    """A submission record kept for a retry. ``root`` holds the bytes it
    sends, the archived ``beril.yaml`` among them (its ``approval`` block is
    read from there at send time); the owner is the login's at send time."""

    project: str
    archive_path: str
    submitted_at: str
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
        "files": files,
    }
    (staging / _PENDING_META).write_text(json.dumps(meta, indent=2), encoding="utf-8")
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
        files=meta["files"],
        root=dest / _PENDING_FILES,
    )


def drop_pending(state_dir: Path, project: str) -> None:
    """Forget the kept record — the server holds it complete."""
    shutil.rmtree(_pending_dir(state_dir, project), ignore_errors=True)
