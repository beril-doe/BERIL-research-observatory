#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openviking==0.4.15",
#     "httpx",
#     "pyyaml",
#     "rich",
# ]
# ///
"""Ingest BERIL context into the knowledge layer.

Two modes, reaching the context store by **different routes**:

**Interactive** (default) — Rich progress output, non-zero exit on failure.
This is the human-facing mode: ``--all``, ``--changed``, ``--project``, ``--docs``.
It drives the OpenViking SDK directly (``observatory_context.openviking_client``)
against the credential ``ContextConfig`` resolves, which is why this script's
PEP-723 header still pins ``openviking``. Only these modes need it.

**Verdict** (``--json``, requires ``--project``) — the *best-effort mirror* used by
``tools/lakehouse_upload.py`` after a successful lakehouse archive, so the
knowledge layer sees the completed project.

The verdict path speaks **only to BERIL**, never to the context backend. It
uploads the staged project to BERIL's ``/api/context/ingest_files`` route with
the personal access token from ``beril login`` and polls the batch to
completion, so a user needs only a BERIL credential — the backend's address,
key, and task vocabulary stay on the server. Two gates must pass first:

  1. the user is logged in to BERIL (``~/.beril/auth.json``), and
  2. the BERIL webapp is reachable and accepts that token.

Both are proved together by an authenticated health call. If either fails we
skip — never fail — because the lakehouse archive, not the context index, is the
source of truth for "submitted".

**Scope note**: the mirror uploads files only. ``apply_project_relations`` and
the ``knowledge/state/`` change manifest are SDK-level operations with no route
equivalent, so the verdict path skips them; a mirrored project's manifest entry
stays whatever the last interactive ``--all``/``--changed`` run recorded. Re-run
an interactive mode to reconcile relations and change tracking.

``--json`` prints a single line of JSON on stdout (always)::

    {"status": "ok"|"skipped"|"failed", "reason": "..."}

and **always exits 0** — it is advisory. The caller reads ``status``/``reason``
and surfaces a WARN on anything other than "ok"; it never treats a non-"ok"
mirror as a submission failure. Nothing else may be written to stdout in this
mode, since the caller parses the last stdout line.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.panel import Panel

from beril_cli import auth_store
from beril_cli.ov_client import OvLinkError, ov_health
from observatory_context.beril_ingest import (
    BerilIngestError,
    ingest_project_files,
)
from observatory_context.config import ContextConfig
from observatory_context.ingest import (
    ingest_all,
    ingest_changed,
    ingest_docs,
    ingest_project,
    resolve_project_dir,
)
from observatory_context.openviking_client import create_client
from observatory_context.progress import RichIngestObserver
from observatory_context.staging import stage_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest BERIL context into the knowledge layer"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true", help="Ingest all selected projects and docs")
    mode.add_argument("--changed", action="store_true", help="Ingest changed selected sources")
    mode.add_argument("--project", help="Ingest one project ID")
    mode.add_argument("--docs", action="store_true", help="Ingest selected central docs")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of projects ingested (only with --all or --changed); "
        "writes a partial manifest so unprocessed projects remain pending",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Best-effort mirror mode (requires --project): upload the staged "
        "project through BERIL's ingest route and poll it to completion, emit a "
        "single-line JSON verdict on stdout, and always exit 0. Used by "
        "tools/lakehouse_upload.py after a successful archive",
    )
    return parser


# --- verdict mode (--json) --------------------------------------------------


def _emit(status: str, reason: str) -> int:
    """Print the single-line JSON verdict. Always exit 0 (advisory)."""
    print(json.dumps({"status": status, "reason": reason}))
    return 0


def _preflight() -> tuple[auth_store.AuthRecord | None, str]:
    """Check the two gates. Return (record, reason); record is None on failure.

    One authenticated health call proves both gates at once: a 200 means the
    BERIL webapp is up and the stored token still authenticates. No
    context-backend credential is checked — the route brokers that itself.
    """
    record = auth_store.load()
    if record is None:
        return None, (
            "not logged in to BERIL (no ~/.beril/auth.json); "
            "run `beril login` to enable the context-service submission"
        )
    try:
        ov_health(record.base_url, record.token)
    except OvLinkError as exc:
        return None, f"BERIL context service health check failed: {exc}"
    return record, "context service available"


def run_mirror(project_id: str) -> int:
    """Best-effort single-project mirror. Never raises; always returns 0.

    Stages the project the same way the interactive path does — so the
    generated ``PROJECT_METADATA.md`` and ``CLAIMS_CONTEXT.md`` are mirrored
    alongside the curated files — then uploads that tree to BERIL as a zip plus
    a manifest and polls the batch to a terminal state.

    A timed-out poll is reported as "skipped", not "failed": the files are
    queued server-side and may well land, so it is not an outcome worth
    marking the submission bad over.

    The server skips files whose content it already holds, so a re-submission
    of unchanged work sends nothing and reports "ok" — there is no batch to
    poll in that case.
    """
    try:
        record, reason = _preflight()
    except Exception as exc:  # unexpected client/transport error
        return _emit("skipped", f"context-service preflight error: {exc}")
    if record is None:
        return _emit("skipped", reason)

    config = ContextConfig.from_env()
    try:
        project_dir = resolve_project_dir(config, project_id)
        staged = stage_project(project_dir, config.staging_dir)
        files = sorted(p for p in staged.rglob("*") if p.is_file())
    except Exception as exc:
        return _emit("failed", f"could not stage {project_id} for submission: {exc}")

    # An empty staging tree means nothing was selected for ingest. Report it
    # rather than posting an empty archive — a silent no-op would look like a
    # successful mirror.
    if not files:
        return _emit("failed", f"{project_id} staged no files to submit")

    try:
        outcome = ingest_project_files(
            record.base_url,
            record.token,
            project=project_id,
            root=staged,
            files=files,
        )
    except BerilIngestError as exc:
        return _emit("failed", f"context-service submission failed: {exc}")
    except Exception as exc:
        return _emit("failed", f"context-service submission failed unexpectedly: {exc}")

    if outcome.ok:
        # "submitted" would be a lie when the server already had every file, so
        # a no-op mirror says so plainly. Both are "ok": the content is there.
        if outcome.batch_id is None:
            return _emit("ok", f"{project_id} already current — {outcome.summary()}")
        return _emit("ok", f"submitted {project_id} to context service ({outcome.summary()})")
    if outcome.timed_out:
        return _emit("skipped", f"{project_id} ingest still in progress — {outcome.summary()}")
    return _emit("failed", f"context-service submission failed: {outcome.summary()}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.limit is not None:
        if not (args.all or args.changed):
            parser.error("--limit can only be used with --all or --changed")
        if args.limit < 1:
            parser.error("--limit must be a positive integer")
    if args.json and args.project is None:
        parser.error("--json requires --project")

    if args.json:
        # Verdict mode: gated, advisory, always exit 0. Resolve the project dir
        # here rather than via parser.error() so a bad ID becomes a JSON "skipped"
        # verdict instead of an argparse exit-2 the caller can't parse.
        try:
            resolve_project_dir(ContextConfig.from_env(), args.project)
        except (FileNotFoundError, ValueError) as exc:
            raise SystemExit(_emit("skipped", f"project not found: {exc}"))
        except Exception as exc:
            raise SystemExit(_emit("skipped", f"could not resolve project: {exc}"))
        raise SystemExit(run_mirror(args.project))

    config = ContextConfig.from_env()
    if args.project is not None:
        try:
            resolve_project_dir(config, args.project)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))

    console = Console()
    started = time.monotonic()
    client = create_client(config)
    try:
        with RichIngestObserver(console=console) as observer:
            if args.all:
                ingest_all(config, client, observer=observer, limit=args.limit)
            elif args.changed:
                ingest_changed(config, client, observer=observer, limit=args.limit)
            elif args.project is not None:
                ingest_project(config, client, args.project, observer=observer)
            elif args.docs:
                ingest_docs(config, client, observer=observer)
        elapsed = time.monotonic() - started
        is_healthy = bool(client.is_healthy()) if hasattr(client, "is_healthy") else True
        summary_style = "green" if is_healthy else "red"
        console.print(
            Panel.fit(
                f"Ingest finished in {elapsed:0.1f}s — server healthy: {is_healthy}",
                title="Done",
                border_style=summary_style,
            )
        )
    finally:
        close = getattr(client, "close", None)
        if close:
            close()


if __name__ == "__main__":
    main()
