"""BERIL CLI — launcher and environment manager for the BERIL Research Observatory."""

from __future__ import annotations

import argparse
import sys

from beril_cli import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="beril",
        description="BERIL Research Observatory — setup, check, and launch your research environment.",
    )
    parser.add_argument("--version", action="version", version=f"beril {__version__}")

    sub = parser.add_subparsers(dest="command")

    # doctor
    sub.add_parser("doctor", help="Check environment health")

    # setup
    sub.add_parser("setup", help="Interactive onboarding wizard")

    # start
    start_parser = sub.add_parser("start", help="Launch a coding agent")
    start_parser.add_argument(
        "--agent",
        choices=["claude", "codex", "gemini"],
        default=None,
        help="Agent to launch (default: from config, or claude)",
    )
    start_parser.add_argument(
        "--skip-onboard",
        action="store_true",
        default=False,
        help="Skip the automatic /berdl_start onboarding prompt",
    )
    start_parser.add_argument(
        "--version",
        default=None,
        metavar="VERSION",
        help="Pin to a specific release tag (e.g. v0.3.4.5). Defaults to the latest tag.",
    )
    start_parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="Only run the local BERIL without fetching the latest release. Overrides any value given in --version."
    )

    # user
    user_parser = sub.add_parser(
        "user",
        help="Show user identity from ~/.config/beril/config.toml",
    )
    user_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit machine-readable JSON",
    )

    # claims
    claims_parser = sub.add_parser(
        "claims",
        help="Build or summarize the per-project claims/evidence ledger",
    )
    claims_parser.add_argument(
        "action",
        choices=["build", "summary"],
        help="build writes claims.json; summary prints the advisory (read-only)",
    )
    claims_parser.add_argument("project", help="Project id under projects/")
    claims_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit machine-readable JSON (summary action)",
    )

    # approve — the human witness for the plan-review checkpoint (records plan_approval)
    approve_parser = sub.add_parser(
        "approve",
        help="Record human approval of a project's RESEARCH_PLAN.md",
    )
    approve_parser.add_argument("project", help="Project id under projects/")
    approve_parser.add_argument(
        "--relayed",
        action="store_true",
        default=False,
        help="Assert the user approved in conversation; the CLI did not witness"
        " it, and the record says so (via: agent-relayed)",
    )

    # auth
    login_parser = sub.add_parser(
        "login",
        help = "Log in to the BERIL server with a personal access token",
    )
    login_parser.add_argument(
        "--token",
        default=None,
        metavar="TOKEN",
        help="Provide the token directly instead of the interactive prompt"
    )
    login_parser.add_argument(
        "--status",
        action="store_true",
        default=False,
        help="Show the current login status, including the current user"
    )
    login_parser.add_argument(
        "--base-url",
        default=None,
        metavar="URL",
        help="Server base URL for login; persisted to ~/.config/beril/config.toml (login only)",
    )

    sub.add_parser(
        "logout",
        help = "Log out of BERIL server, deletes local BERIL auth credentials"
    )

    # ov — link/inspect/export the OpenViking credential (login links it too)
    ov_parser = sub.add_parser(
        "ov",
        help="Link, inspect, or export your OpenViking credential",
    )
    ov_sub = ov_parser.add_subparsers(dest="ov_action", required=True)
    ov_setup = ov_sub.add_parser(
        "setup",
        help="Link OpenViking against your stored login (repair / rotation path)",
    )
    ov_setup.add_argument(
        "--regenerate",
        action="store_true",
        default=False,
        help="Mint a fresh OpenViking key, invalidating the old one",
    )
    ov_sub.add_parser(
        "status",
        help="Show the cached OpenViking credential and probe server health",
    )
    ov_sub.add_parser(
        "print-env",
        help='Emit OPENVIKING_URL / OPENVIKING_API_KEY (eval "$(beril ov print-env)")',
    )

    # runtime-snapshot (settings.json SessionStart hook; reads the hook payload from stdin)
    sub.add_parser(
        "runtime-snapshot",
        help="Write/merge the active project's runtime.json (hook)",
    )

    args, remaining = parser.parse_known_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "doctor":
        from beril_cli.doctor import run_doctor

        return run_doctor()

    if args.command == "setup":
        from beril_cli.setup_cmd import run_setup

        return run_setup()

    if args.command == "start":
        from beril_cli.start import run_start

        return run_start(
            agent=args.agent,
            extra_args=remaining,
            skip_onboard=args.skip_onboard,
            version=args.version,
            dev_mode=args.dev,
        )

    if args.command == "user":
        from beril_cli.user_cmd import run_user

        return run_user(args)

    if args.command == "claims":
        from beril_cli.claims_cmd import run_claims

        return run_claims(args)

    if args.command == "approve":
        from beril_cli.approve_cmd import run_approve

        return run_approve(args)
    if args.command == "login":
        from beril_cli.auth_cmd import run_login
        return run_login(token=args.token, base_url=args.base_url, status=args.status)

    if args.command == "logout":
        from beril_cli.auth_cmd import run_logout
        return run_logout()

    if args.command == "ov":
        from beril_cli.ov_cmd import run_ov
        return run_ov(args)

    if args.command == "runtime-snapshot":
        from beril_cli.audit_cmd import run_runtime_snapshot

        return run_runtime_snapshot(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
