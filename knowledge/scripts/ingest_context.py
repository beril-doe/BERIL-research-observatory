#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openviking",
#     "httpx",
#     "pyyaml",
#     "rich",
# ]
# ///
"""Ingest BERIL context into OpenViking.

Two modes, sharing one ingest code path:

**Interactive** (default) — Rich progress output, non-zero exit on failure.
This is the human-facing mode: ``--all``, ``--changed``, ``--project``, ``--docs``.

**Verdict** (``--json``, requires ``--project``) — the *best-effort mirror* used by
``tools/lakehouse_upload.py`` after a successful lakehouse archive, so the
knowledge layer sees the completed project. Three gates must pass first, all
required:

  1. the BERIL webapp is available,
  2. the user is logged in with a valid credential, and
  3. the context service is reachable and accepts that credential.

(1)+(2) are proved together by an authenticated health call against BERIL;
(3) by the context client's own reachability + auth diagnosis (against the
credential the importer will actually use). If any gate fails we skip — never
fail — because the lakehouse archive, not the context index, is the source of
truth for "submitted".

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
from observatory_context.config import ContextConfig
from observatory_context.ingest import (
    ingest_all,
    ingest_changed,
    ingest_docs,
    ingest_project,
    resolve_project_dir,
)
from observatory_context.openviking_client import create_client, diagnose
from observatory_context.progress import RichIngestObserver


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest BERIL context into OpenViking")
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
        help="Best-effort mirror mode (requires --project): gate on BERIL login + "
        "context-service health, emit a single-line JSON verdict on stdout, and "
        "always exit 0. Used by tools/lakehouse_upload.py after a successful archive",
    )
    return parser


# --- verdict mode (--json) --------------------------------------------------


def _emit(status: str, reason: str) -> int:
    """Print the single-line JSON verdict. Always exit 0 (advisory)."""
    print(json.dumps({"status": status, "reason": reason}))
    return 0


def _preflight() -> tuple[bool, str]:
    """Check the three gates. Return (ok, reason)."""
    # Gates 1+2: authenticated health call against BERIL. A 200 proves the
    # webapp is up and the stored token still authenticates.
    record = auth_store.load()
    if record is None:
        return False, (
            "not logged in to BERIL (no ~/.beril/auth.json); "
            "run `beril login` to enable the context-service submission"
        )
    try:
        ov_health(record.base_url, record.token)
    except OvLinkError as exc:
        return False, f"BERIL context service health check failed: {exc}"

    # Gate 3: reachability + client-auth against the context service the way the
    # importer will reach it (ContextConfig resolves the cached credential).
    diag = diagnose(ContextConfig.from_env())
    if not diag.ok:
        return False, f"context service not ready ({diag.verdict}): {diag.detail}"
    return True, "context service available"


def run_mirror(project_id: str) -> int:
    """Best-effort single-project mirror. Never raises; always returns 0.

    Shares `ingest_project` with the interactive path — the difference is the
    gating, the machine-readable verdict, and the promise never to fail the
    caller. No observer is passed: Rich output would pollute the stdout line
    the caller parses.
    """
    try:
        ok, reason = _preflight()
    except Exception as exc:  # unexpected client/transport error
        return _emit("skipped", f"context-service preflight error: {exc}")
    if not ok:
        return _emit("skipped", reason)

    config = ContextConfig.from_env()
    try:
        client = create_client(config)
    except (SystemExit, Exception) as exc:
        # create_client raises SystemExit on an unreachable server — that's a
        # BaseException, so it must be named explicitly; a bare `except
        # Exception` would let it propagate and kill the caller's upload. The
        # preflight should have caught this, but guard against the race.
        return _emit("skipped", f"context service became unreachable: {exc}")

    try:
        ingest_project(config, client, project_id)
    except Exception as exc:
        return _emit("failed", f"context-service submission failed: {exc}")
    finally:
        close = getattr(client, "close", None)
        if close:
            try:
                close()
            except Exception:
                pass

    return _emit("ok", f"submitted {project_id} to context service")


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
