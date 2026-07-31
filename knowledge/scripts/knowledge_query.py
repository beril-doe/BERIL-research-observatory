#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openviking",
#     "pyyaml",
#     "boto3",
# ]
# ///
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from observatory_context import berdl_fallback, fallback
from observatory_context.config import ContextConfig
from observatory_context.openviking_client import (
    create_client,
    diagnose,
    format_diagnosis,
    server_reachable,
)
from observatory_context.query import (
    format_find_text,
    run_command,
    target_uri_for_find,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query BERIL context in OpenViking")
    commands = parser.add_subparsers(dest="command", required=True)

    find = commands.add_parser("find", help="Semantic search")
    find.add_argument("query", help="Search query")
    scope = find.add_mutually_exclusive_group()
    scope.add_argument("--project", help="Search one project ID")
    scope.add_argument("--docs", action="store_true", help="Search central docs")
    scope.add_argument("--target-uri", help="Search a raw OpenViking target URI")
    find.add_argument("--limit", type=int, default=10, help="Maximum results")
    find.add_argument("--filter", help="Raw JSON metadata filter (OV filter tree)")
    find.add_argument("--score-threshold", type=float, help="Minimum score")
    find.add_argument("--since", help="Lower time bound (ISO date or 7d/2w)")
    find.add_argument("--until", help="Upper time bound (ISO date or 7d/2w)")
    find.add_argument(
        "--time-field",
        choices=["updated_at", "created_at"],
        help="Time field for since/until",
    )
    find.add_argument("--json", action="store_true", help="Print JSON")

    grep = commands.add_parser("grep", help="Exact pattern search across resources")
    grep.add_argument("pattern", help="Pattern to match")
    grep.add_argument(
        "--uri",
        default="viking://resources/",
        help="URI subtree to search (default: viking://resources/)",
    )
    grep.add_argument("-i", "--case-insensitive", action="store_true")
    grep.add_argument("--exclude-uri", help="URI subtree to exclude")
    grep.add_argument("--node-limit", type=int, help="Max matching nodes")

    glob = commands.add_parser("glob", help="URI pattern enumeration")
    glob.add_argument("pattern", help="Glob pattern (e.g. viking://resources/projects/*/)")
    glob.add_argument("--uri", default="viking://", help="Root URI")

    ls = commands.add_parser("ls", help="List directory contents")
    ls.add_argument("uri", help="Directory URI")
    ls.add_argument("--simple", action="store_true", help="Path list only")
    ls.add_argument("-r", "--recursive", action="store_true")

    tree = commands.add_parser("tree", help="Print resource hierarchy")
    tree.add_argument("uri", help="Root URI")
    tree.add_argument("--node-limit", type=int, default=1000)

    stat = commands.add_parser("stat", help="Resource metadata")
    stat.add_argument("uri", help="Resource URI")

    relations = commands.add_parser("relations", help="List relations for a resource")
    relations.add_argument("uri", help="Resource URI")

    link = commands.add_parser("link", help="Create relation(s) between resources")
    link.add_argument("from_uri", help="Source URI")
    link.add_argument("to_uris", nargs="+", help="Target URI(s)")
    link.add_argument("--reason", default="", help="Optional reason for the relation")

    unlink = commands.add_parser("unlink", help="Remove a relation")
    unlink.add_argument("from_uri", help="Source URI")
    unlink.add_argument("to_uri", help="Target URI")

    overview = commands.add_parser("overview", help="Print a resource overview")
    overview.add_argument("uri", help="Resource URI")

    read = commands.add_parser("read", help="Print a resource")
    read.add_argument("uri", help="Resource URI")

    doctor = commands.add_parser(
        "doctor", help="Check OpenViking reachability and auth (server vs. key)"
    )
    doctor.add_argument("--json", action="store_true", help="Print JSON")

    return parser


def _berdl_then_local(config, uri, berdl_fn, local_fn):
    """Try the BERDL lakehouse archive first, then the local working tree.

    ``find``/``read``/``overview`` each fetch specific resources, so they can be
    served from the submitted lakehouse copy when OpenViking is down. If that
    tier is unavailable — no credentials, unreachable, unauthorized, or the
    resource/scope isn't archived — fall through to local. A per-tier banner
    tells the user which source actually answered. Returns whatever the tier
    function returns (str for read/overview, result dict for find).
    """
    try:
        result = berdl_fn(config, uri)
        print(berdl_fallback.BANNER, file=sys.stderr)
        return result
    except berdl_fallback.BerdlUnavailable as exc:
        print(
            f"⚠ BERDL lakehouse unavailable ({exc}) — using local working tree.",
            file=sys.stderr,
        )
        print(fallback.BANNER.format(url=config.openviking_url), file=sys.stderr)
        return local_fn(config, uri)


def _berdl_or_notice(config, args, berdl_fn):
    """Serve a structural command from BERDL, or print the degraded notice.

    ``ls``/``tree``/``stat``/``glob`` have no local equivalent, so — unlike
    read/find/grep — an unavailable lakehouse degrades to the same "unavailable"
    notice the fully-offline path prints, not to a local search. Returns True if
    BERDL answered (output already printed), False if it degraded to the notice.
    """
    try:
        result = berdl_fn(config)
    except berdl_fallback.BerdlUnavailable as exc:
        print(
            f"⚠ BERDL lakehouse unavailable ({exc}); {args.command} has no local "
            "fallback — start OpenViking for this command.",
            file=sys.stderr,
        )
        return False
    print(berdl_fallback.BANNER, file=sys.stderr)
    print(json.dumps(result, indent=2, default=str))
    return True


def _run_fallback(args, config: ContextConfig) -> None:
    # find/grep/read/overview all try BERDL first, then fall through to local.
    # find/grep search only the curated corpus (the files local search covers),
    # so the per-query download stays bounded. link/unlink and structural
    # queries (ls/tree/stat/...) have no degraded path and hit the else branch.
    # Each branch prints its own banner so the user sees which tier answered.
    if args.command == "find":
        target_uri = target_uri_for_find(
            project=args.project, docs=args.docs, target_uri=args.target_uri
        )
        result = _berdl_then_local(
            config,
            target_uri,
            lambda cfg, uri: berdl_fallback.berdl_find(cfg, args.query, uri, args.limit),
            lambda cfg, uri: fallback.local_find(cfg, args.query, uri, args.limit),
        )
        print(json.dumps(result, default=str) if args.json else format_find_text(result))
    elif args.command == "grep":
        result = _berdl_then_local(
            config,
            args.uri,
            lambda cfg, uri: berdl_fallback.berdl_grep(
                cfg,
                args.pattern,
                uri,
                case_insensitive=args.case_insensitive,
                exclude_uri=args.exclude_uri,
                node_limit=args.node_limit,
            ),
            lambda cfg, uri: fallback.local_grep(
                cfg,
                args.pattern,
                uri,
                case_insensitive=args.case_insensitive,
                exclude_uri=args.exclude_uri,
                node_limit=args.node_limit,
            ),
        )
        print(json.dumps(result, indent=2, default=str))
    elif args.command == "read":
        print(_berdl_then_local(config, args.uri, berdl_fallback.berdl_read, fallback.local_read))
    elif args.command == "overview":
        print(
            _berdl_then_local(
                config, args.uri, berdl_fallback.berdl_overview, fallback.local_overview
            )
        )
    elif args.command == "ls":
        if not _berdl_or_notice(
            config,
            args,
            lambda cfg: berdl_fallback.berdl_ls(
                cfg, args.uri, simple=args.simple, recursive=args.recursive
            ),
        ):
            print(fallback.DEGRADED_NOTICE.format(command=args.command), file=sys.stderr)
    elif args.command == "tree":
        if not _berdl_or_notice(
            config,
            args,
            lambda cfg: berdl_fallback.berdl_tree(cfg, args.uri, node_limit=args.node_limit),
        ):
            print(fallback.DEGRADED_NOTICE.format(command=args.command), file=sys.stderr)
    elif args.command == "stat":
        if not _berdl_or_notice(
            config, args, lambda cfg: berdl_fallback.berdl_stat(cfg, args.uri)
        ):
            print(fallback.DEGRADED_NOTICE.format(command=args.command), file=sys.stderr)
    elif args.command == "glob":
        if not _berdl_or_notice(
            config, args, lambda cfg: berdl_fallback.berdl_glob(cfg, args.pattern, args.uri)
        ):
            print(fallback.DEGRADED_NOTICE.format(command=args.command), file=sys.stderr)
    else:
        # relations/link/unlink and any other command have no BERDL or local
        # equivalent in degraded mode.
        print(fallback.BANNER.format(url=config.openviking_url), file=sys.stderr)
        print(fallback.DEGRADED_NOTICE.format(command=args.command), file=sys.stderr)


def _run_doctor(args, config: ContextConfig) -> int:
    diag = diagnose(config)
    if args.json:
        print(
            json.dumps(
                {
                    "verdict": diag.verdict,
                    "url": diag.url,
                    "reachable": diag.reachable,
                    "detail": diag.detail,
                    "remedy": diag.remedy,
                    "server": diag.server,
                },
                indent=2,
                default=str,
            )
        )
    else:
        print(format_diagnosis(diag))
    return 0 if diag.ok else 1


def main() -> None:
    args = build_parser().parse_args()
    config = ContextConfig.from_env()
    if args.command == "doctor":
        sys.exit(_run_doctor(args, config))
    if not server_reachable(config):
        _run_fallback(args, config)
        return
    client = create_client(config)
    try:
        code = run_command(args, client)
    finally:
        close = getattr(client, "close", None)
        if close:
            close()
    sys.exit(code)


if __name__ == "__main__":
    main()
