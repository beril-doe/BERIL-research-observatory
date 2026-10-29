"""beril context — search and browse the BERIL context layer.

  beril context find QUERY       semantic search (whole corpus unless scoped)
  beril context ls [ADDRESS]     list what is stored at an address
  beril context grep PATTERN     exact-pattern search
  beril context pitfalls [Q]     known gotchas: project memories + central archive
  beril context discoveries [Q]  findings, with stale duplicates suppressed
  beril context doctor           check the login, BERIL, and the context layer

Every result names a resource by **address**: ``<owner>/<project>/<path>``
(central docs live under ``beril/docs/``). Pass one back with ``--address`` —
or as ``ls``'s argument — to read there. Without an address, scope a read with
``--project`` (your own project), ``--owner``, ``--all-owners``, ``--path``,
or ``--docs`` for the central docs.

Uses the stored BERIL login (``beril login``); there is no offline fallback —
when BERIL is unreachable these commands fail and say so.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from beril_cli import auth_store
from beril_cli.context_client import ContextClient, ContextError, Scope

# Central docs (pitfalls, discoveries, performance, research ideas) live under
# the house account.
_DOCS = Scope(owner="beril", project="docs")

# find's result count when --limit is omitted, and the most it may ask for.
# find is ranked, so a full page means "these are the best", not "these are
# all"; the server reports in ``total`` whether more lie past the limit.
_DEFAULT_FIND_LIMIT = 10
_MAX_FIND_LIMIT = 200
# The server's grep budget when --node-limit is omitted. grep returns at most
# this many matches and reports only how many it returned, so reaching it is
# the only sign that matches were cut off.
_DEFAULT_GREP_LIMIT = 256
# The server's listing budget when --node-limit is omitted.
_DEFAULT_LS_LIMIT = 1000


def add_parser(sub: argparse._SubParsersAction) -> None:
    """Register ``beril context`` and its subcommands on the top-level parser."""
    context = sub.add_parser(
        "context",
        help="Search and browse the BERIL context layer",
        description=__doc__.replace("``", "").replace("**", ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    actions = context.add_subparsers(dest="context_action", required=True)

    find = actions.add_parser("find", help="Semantic search")
    find.add_argument("query", help="What to search for")
    _add_scope(find)
    find.add_argument(
        "--limit", type=int,
        help=f"Maximum results, best first (default {_DEFAULT_FIND_LIMIT}, up to {_MAX_FIND_LIMIT})",
    )
    find.add_argument("--score-threshold", type=float, help="Minimum score")
    find.add_argument("--since", help="Lower time bound (ISO date, or 7d / 2w)")
    find.add_argument("--until", help="Upper time bound (ISO date, or 7d / 2w)")
    find.add_argument(
        "--time-field", choices=["updated_at", "created_at"],
        help="Which timestamp --since/--until bound",
    )
    find.add_argument(
        "--read-content", action="store_true",
        help="Print each hit's full text, not just its abstract",
    )
    _add_json(find)

    ls = actions.add_parser("ls", help="List what is stored at an address")
    ls.add_argument(
        "target", nargs="?", metavar="ADDRESS",
        help="Where to list (owner/project/path). Omitted: your own projects.",
    )
    _add_scope(ls, address_flag=False)
    ls.add_argument("-r", "--recursive", action="store_true")
    ls.add_argument("--simple", action="store_true", help="Addresses only")
    ls.add_argument(
        "--node-limit", type=int,
        help="Maximum entries (default 1000, up to 10000); a warning says when it is reached",
    )
    ls.add_argument(
        "--depth", type=int,
        help="With -r: how many levels below the address to list (default: all)",
    )
    _add_json(ls)

    grep = actions.add_parser("grep", help="Exact-pattern search")
    grep.add_argument("pattern", help="Pattern to match")
    _add_scope(grep)
    grep.add_argument("-i", "--case-insensitive", action="store_true")
    grep.add_argument("--exclude", metavar="ADDRESS", help="An address to leave out")
    grep.add_argument(
        "--node-limit", type=int,
        help="Maximum matches (default 256, up to 10000); a warning says when it is reached",
    )
    _add_json(grep)

    for name, help_text in (
        ("pitfalls", "Known gotchas: project memories and the central archive"),
        ("discoveries", "Findings, current copies only (stale duplicates suppressed)"),
    ):
        p = actions.add_parser(name, help=help_text)
        p.add_argument(
            "query", nargs="?",
            help="Error text, table name, or description. Omitted: list them all.",
        )
        p.add_argument(
            "--project",
            help="Narrow project memories to one project (yours unless --owner)",
        )
        p.add_argument(
            "--owner",
            help="Narrow project memories to one owner's projects (ORCiD)",
        )
        p.add_argument(
            "--exact", action="store_true",
            help="Match tokens literally instead of semantically",
        )
        p.add_argument("--limit", type=int, help="Maximum documents (default 10)")
        _add_json(p)

    doctor = actions.add_parser(
        "doctor", help="Check the login, BERIL, and the context layer"
    )
    _add_json(doctor)


def _add_scope(parser: argparse.ArgumentParser, *, address_flag: bool = True) -> None:
    group = parser.add_argument_group("scope")
    if address_flag:
        group.add_argument(
            "--address", help="An address from an earlier result (owner/project/path)"
        )
    group.add_argument("--project", help="A project (your own, unless --owner)")
    group.add_argument("--owner", help="An owner's ORCiD")
    group.add_argument("--path", help="A path within --project")
    group.add_argument(
        "--all-owners", action="store_true", help="Every owner's projects"
    )
    group.add_argument(
        "--docs", action="store_true", help="The central docs (beril/docs)"
    )


def _add_json(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response")


def run_context(args: argparse.Namespace) -> int:
    action = args.context_action
    if action == "doctor":
        return _run_doctor(args)
    handler = _HANDLERS.get(action)
    if handler is None:
        print(
            "Usage: beril context {find|ls|grep|pitfalls|discoveries|doctor}",
            file=sys.stderr,
        )
        return 1

    record = auth_store.load()
    if record is None:
        print("Not logged in. Run `beril login` first.", file=sys.stderr)
        return 1
    try:
        with ContextClient(record.base_url, record.token) as client:
            handler(client, args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except ContextError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


def _scope(args: argparse.Namespace) -> Scope:
    """The scope the flags name; ``ValueError`` when they contradict."""
    address = getattr(args, "address", None) or getattr(args, "target", None)
    explicit = [
        flag for flag, value in (
            ("--project", args.project), ("--owner", args.owner),
            ("--path", args.path), ("--all-owners", args.all_owners),
        ) if value
    ]
    if address and (explicit or args.docs):
        raise ValueError(
            "an address already names owner, project and path; "
            f"drop {', '.join(explicit + (['--docs'] if args.docs else []))}"
        )
    if args.docs and (args.project or args.owner or args.all_owners):
        raise ValueError("--docs names the central docs; drop --project/--owner/--all-owners")
    if args.owner and args.all_owners:
        raise ValueError("--owner names one owner and --all-owners every owner; pick one")
    if args.path and not (args.project or args.docs):
        raise ValueError("--path is a path within a project; give --project too")
    if address:
        return Scope.from_address(address)
    if args.docs:
        return Scope(owner=_DOCS.owner, project=_DOCS.project, path=args.path)
    return Scope(
        project=args.project, owner=args.owner, path=args.path,
        all_owners=args.all_owners,
    )


def _find(client: ContextClient, args: argparse.Namespace) -> None:
    result = client.find(
        args.query,
        _scope(args),
        limit=args.limit,
        score_threshold=args.score_threshold,
        since=args.since,
        until=args.until,
        time_field=args.time_field,
        read_content=args.read_content,
    )
    print(_dump(result) if args.json else format_find(result))
    # On stderr, so the output — text or JSON — stays parseable. A ranked page
    # that reads as the whole answer leads to "nobody has done this".
    shown = len(result.get("results") or [])
    if (result.get("total") or 0) > shown:
        print(
            f"note: showing the top {shown}; more ranked results lie past the limit. "
            f"Raise --limit (up to {_MAX_FIND_LIMIT}), narrow the scope, or use grep "
            "to find every literal match.",
            file=sys.stderr,
        )


def _ls(client: ContextClient, args: argparse.Namespace) -> None:
    if args.depth is not None and not args.recursive:
        raise ValueError("--depth applies to a recursive listing; add -r")
    listed = client.ls(
        _scope(args), recursive=args.recursive, simple=args.simple,
        node_limit=args.node_limit, depth=args.depth,
    )
    print(_dump(listed) if args.json else format_ls(listed))
    # On stderr, so the output — text or JSON — stays parseable. A listing that
    # looks complete but is not leads to "no such document" conclusions.
    limit = args.node_limit or _DEFAULT_LS_LIMIT
    if len(listed) >= limit:
        print(
            f"warning: the listing stopped at the {limit}-entry limit and may be "
            "incomplete; raise --node-limit (up to 10000) or list a narrower address.",
            file=sys.stderr,
        )
    if args.depth is not None and _reaches_depth(listed, args.depth):
        print(
            f"warning: directories at depth {args.depth} were not expanded; "
            "raise --depth to see what is below them.",
            file=sys.stderr,
        )


def _reaches_depth(listed: list, depth: int) -> bool:
    """Whether a recursive listing has a directory at its depth limit — whose
    contents were therefore not listed. Needs entries with ``rel_path``, which
    a ``--simple`` listing does not have."""
    return any(
        isinstance(e, dict) and e.get("isDir")
        and len(str(e.get("rel_path") or "").strip("/").split("/")) >= depth
        for e in listed
    )


def _grep(client: ContextClient, args: argparse.Namespace) -> None:
    exclude = Scope.from_address(args.exclude) if args.exclude else None
    result = client.grep(
        args.pattern, _scope(args), exclude=exclude,
        case_insensitive=args.case_insensitive, node_limit=args.node_limit,
    )
    print(_dump(result) if args.json else format_grep(result))
    limit = args.node_limit or _DEFAULT_GREP_LIMIT
    if len(result.get("matches") or []) >= limit:
        # On stderr, so the output — text or JSON — stays parseable.
        print(
            f"warning: results stopped at the {limit}-match limit and may be "
            "incomplete; raise --node-limit (up to 10000) or narrow the scope.",
            file=sys.stderr,
        )


def _documents(kind: str) -> Callable[[ContextClient, argparse.Namespace], None]:
    def run(client: ContextClient, args: argparse.Namespace) -> None:
        result = getattr(client, kind)(
            args.query, project=args.project, owner=args.owner,
            exact=args.exact, limit=args.limit,
        )
        print(_dump(result) if args.json else format_documents(result, kind))
    return run


_HANDLERS: dict[str, Callable[[ContextClient, argparse.Namespace], None]] = {
    "find": _find,
    "ls": _ls,
    "grep": _grep,
    "pitfalls": _documents("pitfalls"),
    "discoveries": _documents("discoveries"),
}


# --- doctor -----------------------------------------------------------------


def _run_doctor(args: argparse.Namespace) -> int:
    """Check, in order: a stored login, BERIL reachable, the token accepted,
    and the context layer healthy. Exit 0 only when all four pass.

    The identity reported is the one BERIL gives for the token, not the one
    cached at login: reads default to that identity's projects, so a stale
    cache would otherwise mislead.
    """
    record = auth_store.load()
    report: dict[str, Any] = {
        "verdict": "ok",
        "base_url": record.base_url if record else None,
        "user": None,
        "detail": None,
        "remedy": None,
    }
    if record is None:
        report.update(
            verdict="not_logged_in", detail="No stored BERIL login.",
            remedy="Run `beril login`.",
        )
    else:
        try:
            with ContextClient(record.base_url, record.token, timeout=15.0) as client:
                report["user"] = client.whoami().get("orcid_id")
                status = client.health().get("status")
        except ContextError as e:
            if e.auth_failed:
                report.update(
                    verdict="auth_failed", detail="BERIL rejected the stored token.",
                    remedy="Run `beril login` to log in again.",
                )
            elif report["user"]:
                # BERIL answered whoami, so the network and the server are
                # fine; it is the context route that failed (a gateway error
                # page, a timeout). That is the service, not the user's setup.
                report.update(
                    verdict="unavailable",
                    detail=f"BERIL is up, but its context layer did not answer: {e}",
                    remedy="Try again shortly; if it persists, tell a BERIL admin.",
                )
            else:
                report.update(
                    verdict="unreachable", detail=str(e),
                    remedy="Check your network, or the BERIL server's status.",
                )
        else:
            if status != "ok":
                report.update(
                    verdict="unavailable",
                    detail="BERIL is up, but its context layer is not answering.",
                    remedy="Try again shortly; if it persists, tell a BERIL admin.",
                )
            elif report["user"] and report["user"] != record.orcid_id:
                report["detail"] = (
                    f"Note: your login was saved as {record.orcid_id}, but BERIL "
                    f"knows this token as {report['user']}. Run `beril login` to "
                    "refresh it."
                )

    if args.json:
        print(_dump(report))
    else:
        print(format_doctor(report))
    return 0 if report["verdict"] == "ok" else 1


# --- text formats -------------------------------------------------------------


def format_find(result: dict) -> str:
    """``N result(s)``, then per hit: address, score, abstract — the shape the
    skills already read — plus the full text when it was asked for. ``N`` is
    the hits shown; ``total`` can be larger (see ``_find``)."""
    hits = result.get("results") or []
    lines = [f"{len(hits)} result(s)"]
    for hit in hits:
        lines += [
            "",
            hit.get("address") or "",
            f"score: {float(hit.get('score') or 0.0):.3f}",
            hit.get("text") or "",
        ]
        if hit.get("match_reason"):
            lines.append(f"match_reason: {hit['match_reason']}")
        if hit.get("content") is not None:
            lines += ["--- content ---", hit["content"], "--- end ---"]
    return "\n".join(lines)


def format_ls(listed: list) -> str:
    """One address per line; directories end in ``/``."""
    lines = []
    for entry in listed:
        if isinstance(entry, str):
            lines.append(entry)
        elif isinstance(entry, dict):
            address = entry.get("address") or entry.get("name") or ""
            lines.append(address + ("/" if entry.get("isDir") else ""))
    return "\n".join(lines) if lines else "(empty)"


def format_grep(result: dict) -> str:
    """``address:line: text`` per match, then a count of matches and of the
    files they are in.

    The file count is the distinct addresses among the matches. The store's
    own ``files_scanned`` is not used: depending on how it searched, it is
    either the files scanned or the files that matched, and saying "scanned"
    made a no-match search read as "nothing was searched".
    """
    matches = result.get("matches") or []
    lines = [
        f"{m.get('address') or ''}:{m.get('line')}: {(m.get('content') or '').strip()}"
        for m in matches
    ]
    count = result.get("count", len(matches))
    files = len({m.get("address") for m in matches})
    lines.append(f"{count} match(es)" + (f" in {files} file(s)" if count and files else ""))
    return "\n".join(lines)


def format_documents(result: dict, kind: str) -> str:
    """Pitfall or discovery documents: address, origin, score, excerpts."""
    docs = result.get("results") or []
    total = result.get("total", len(docs))
    header = f"{len(docs)} of {total} {kind} document(s)"
    if result.get("suppressed"):
        header += f"; {result['suppressed']} stale duplicate(s) suppressed"
    lines = [header]
    for doc in docs:
        origin = doc.get("origin") or ""
        if doc.get("project"):
            origin += f" ({doc['project']})"
        score = doc.get("score")
        lines += [
            "",
            doc.get("address") or "",
            f"origin: {origin}" + (f"  score: {float(score):.3f}" if score is not None else ""),
        ]
        lines += [f"  > {_one_line(x)}" for x in doc.get("excerpts") or []]
    return "\n".join(lines)


def format_doctor(report: dict) -> str:
    status = "OK" if report["verdict"] == "ok" else report["verdict"].upper()
    lines = [f"Context layer: {status}"]
    if report.get("base_url"):
        lines.append(f"BERIL: {report['base_url']}")
    if report.get("user"):
        lines.append(f"Logged in as: {report['user']}")
    if report.get("detail"):
        lines.append(report["detail"])
    if report.get("remedy"):
        lines.append(f"Fix: {report['remedy']}")
    return "\n".join(lines)


def _one_line(text: str, width: int = 200) -> str:
    flat = " ".join(str(text).split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def _dump(value: Any) -> str:
    return json.dumps(value, indent=2, default=str)
