#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx",
#     "pyyaml",
# ]
# ///
"""Index the repo's projects into the context layer, each owned by its author.

An admin tool. For the projects that predate ``/submit``: each is staged the
way the ``/submit`` mirror stages it and uploaded to BERIL's admin import
route, which lands it in its **owner's** namespace — as if they had submitted
it themselves. Ownership is decided on the server, by the repo importer's rule
(first author ORCiD in beril.yaml, else in an Authors section); this script
only reports it.

Needs an admin's ``beril login`` against the target server, and the repo
import to have run there (``/admin/import``), since it creates the project rows
whose owners are used.

    uv run knowledge/scripts/import_projects.py --all --dry-run   # who owns what; nothing written
    uv run knowledge/scripts/import_projects.py --all             # import everything importable
    uv run knowledge/scripts/import_projects.py alpha beta        # just these

Per project the outcome is one of: imported, already current (nothing changed
since the last import), flagged (no author ORCiD — fix the project's authors,
re-run the repo import), not imported (the repo import hasn't seen it),
in progress (still indexing when the wait ran out — it may well land), or
failed. Safe to re-run: unchanged files are skipped.

A project the repo import has re-owned is written to its new owner, and the
copy under the previous owner is removed, one file per request; anything not
removed is retried on the next run.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import httpx  # noqa: E402

from beril_cli import auth_store  # noqa: E402
from observatory_context.beril_ingest import (  # noqa: E402
    BerilIngestError,
    ingest_project_files,
)
from observatory_context.staging import stage_project  # noqa: E402

IMPORT_PATH = "/api/admin/context/import_files"
IMPORT_STATUS_PATH = "/api/admin/context/import_status"
RETIRE_PATH = "/api/admin/context/retire_file"


class Abort(Exception):
    """A problem with the whole run (login, permission), not one project."""


@dataclass
class Outcome:
    project: str
    status: str  # imported | current | flagged | not_imported | in_progress | failed | would_import
    detail: str = ""
    owner: str | None = None


def owner_of(http: httpx.Client, base_url: str, token: str, project: str) -> Outcome:
    """Ask the server who owns ``project`` (a dry-run import)."""
    try:
        resp = http.post(
            base_url.rstrip("/") + IMPORT_PATH,
            data={"project": project, "dry_run": "true"},
            headers={"Authorization": f"Bearer {token}"},
        )
    except httpx.HTTPError as exc:
        raise Abort(f"could not reach {base_url}: {exc}") from exc
    if resp.status_code == 401:
        raise Abort("your BERIL token was rejected — run `beril login`.")
    if resp.status_code == 403:
        raise Abort("this login is not a BERIL administrator.")
    detail = _detail(resp)
    if resp.status_code == 404:
        return Outcome(project, "not_imported", detail)
    if resp.status_code == 409:
        return Outcome(project, "flagged", detail)
    if not resp.is_success:
        return Outcome(project, "failed", f"HTTP {resp.status_code}: {detail}")
    return Outcome(project, "would_import", owner=resp.json().get("owner_orcid"))


def import_one(
    http: httpx.Client, base_url: str, token: str, project_dir: Path, *, force: bool, wait: float
) -> Outcome:
    planned = owner_of(http, base_url, token, project_dir.name)
    if planned.status != "would_import":
        return planned
    with tempfile.TemporaryDirectory() as tmp:
        try:
            staged = stage_project(project_dir, Path(tmp))
            files = sorted(p for p in staged.rglob("*") if p.is_file())
        except Exception as exc:  # staging reads arbitrary project files
            return Outcome(project_dir.name, "failed", f"could not stage: {exc}", planned.owner)
        if not files:
            return Outcome(project_dir.name, "failed", "staged no files", planned.owner)
        try:
            outcome = ingest_project_files(
                base_url,
                token,
                project=project_dir.name,
                root=staged,
                files=files,
                client=http,
                ingest_path=IMPORT_PATH,
                status_path=IMPORT_STATUS_PATH,
                form={"force": "true"} if force else None,
                max_wait=wait,
            )
        except BerilIngestError as exc:
            return Outcome(project_dir.name, "failed", str(exc), planned.owner)
    records = outcome.response.get("retire_records") or []
    detail = outcome.summary()
    # The previous owner's copy goes only once this one has fully landed —
    # otherwise a failed or unfinished import could leave no copy at all. (The
    # server refuses an early retirement too.) Kept copies are retried next run.
    if records and not outcome.ok:
        detail += f"; previous owner's copy kept ({len(records)} file(s)) until this import lands"
        records = []
    retired, retire_failed = retire(http, base_url, token, records)
    if retired or retire_failed:
        detail += f"; previous owner's copy: {retired} removed"
        if retire_failed:
            detail += f", {retire_failed} not removed (re-run to retry)"
    if retire_failed:
        return Outcome(project_dir.name, "failed", detail, planned.owner)
    if outcome.ok:
        status = "current" if outcome.batch_id is None else "imported"
        return Outcome(project_dir.name, status, detail, planned.owner)
    if outcome.timed_out:
        return Outcome(project_dir.name, "in_progress", detail, planned.owner)
    return Outcome(project_dir.name, "failed", detail, planned.owner)


def retire(http: httpx.Client, base_url: str, token: str, records: list[str]) -> tuple[int, int]:
    """Remove what a re-owned project left under its previous owner, one file
    per call (each delete is confirmed by the store, which takes a while).

    Returns ``(removed, not_removed)``. A file not removed stays marked
    pending on the server and is planned again on the next import.
    """
    removed = failed = 0
    for record in records:
        try:
            resp = http.post(
                f"{base_url.rstrip('/')}{RETIRE_PATH}/{record}",
                headers={"Authorization": f"Bearer {token}"},
            )
            ok = resp.is_success and resp.json().get("status") == "removed"
        except (httpx.HTTPError, ValueError):
            ok = False
        removed, failed = (removed + 1, failed) if ok else (removed, failed + 1)
    return removed, failed


def _detail(resp: httpx.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text.strip()[:200]
    return str(body.get("detail")) if isinstance(body, dict) and body.get("detail") else ""


def _project_dirs(names: list[str], all_projects: bool) -> list[Path]:
    root = REPO_ROOT / "projects"
    if all_projects:
        return sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith("."))
    dirs = []
    for name in names:
        d = root / name
        if "/" in name or not d.is_dir():
            raise Abort(f"no project directory projects/{name}")
        dirs.append(d)
    return dirs


def report(outcomes: list[Outcome]) -> None:
    width = max((len(o.project) for o in outcomes), default=10)
    for o in outcomes:
        owner = o.owner or "-"
        print(f"{o.project:<{width}}  {o.status:<13} {owner:<20} {o.detail}".rstrip())
    counts: dict[str, int] = {}
    for o in outcomes:
        counts[o.status] = counts.get(o.status, 0) + 1
    print("\n" + ", ".join(f"{n} {s}" for s, n in sorted(counts.items())))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Index repo projects into the context layer under their owners (admin)."
    )
    parser.add_argument("projects", nargs="*", help="Project directory names under projects/")
    parser.add_argument("--all", action="store_true", help="Every project under projects/")
    parser.add_argument(
        "--dry-run", action="store_true", help="Report each project's owner; write nothing"
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-send files even if unchanged since the last import"
    )
    parser.add_argument(
        "--wait", type=float, default=600.0,
        help="Seconds to wait for each project to finish indexing (default 600; 0 = don't wait)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if bool(args.projects) == args.all:
        print("error: name projects, or pass --all (not both).", file=sys.stderr)
        return 2
    record = auth_store.load()
    if record is None:
        print("error: not logged in — run `beril login` as an administrator.", file=sys.stderr)
        return 1
    outcomes: list[Outcome] = []
    try:
        dirs = _project_dirs(args.projects, args.all)
        # Long enough for one store-confirmed delete or a large upload; each
        # request does one bounded piece of work.
        with httpx.Client(timeout=300.0) as http:
            for d in dirs:
                if args.dry_run:
                    outcome = owner_of(http, record.base_url, record.token, d.name)
                else:
                    outcome = import_one(
                        http, record.base_url, record.token, d, force=args.force, wait=args.wait
                    )
                outcomes.append(outcome)
                print(f"{outcome.project}: {outcome.status}", file=sys.stderr)
    except Abort as exc:
        if outcomes:
            report(outcomes)
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"\n{record.base_url}" + (" (dry run)" if args.dry_run else ""))
    report(outcomes)
    return 1 if any(o.status == "failed" for o in outcomes) else 0


if __name__ == "__main__":
    sys.exit(main())
