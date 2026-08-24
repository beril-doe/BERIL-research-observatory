#!/usr/bin/env python3
"""Resolve BERDL MinIO credentials from local env or BERDL remote context."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get BERDL MinIO credentials.")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Optional dotenv file to load before reading environment variables.",
    )
    parser.add_argument(
        "--bootstrap-remote",
        action="store_true",
        help="Run berdl-remote login and spawn before reading remote env vars.",
    )
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Print output as shell exports instead of JSON.",
    )
    return parser.parse_args()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def parse_remote_json(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


DEFAULT_ENDPOINT_URL = "https://minio.berdl.kbase.us"

# BERDL renamed these from MINIO_* to S3_* and no consumer was updated, which is
# what this script fixes. Verified on a pod 2026-08-14: only S3_ACCESS_KEY,
# S3_SECRET_KEY, S3_ENDPOINT_URL and S3_SECURE are present; no MINIO_* variable
# exists. Per @mikacashman on #380, pods cycle, so there is no image left to be
# backwards compatible with and carrying a fallback only implies otherwise.
ACCESS_KEY = "S3_ACCESS_KEY"
SECRET_KEY = "S3_SECRET_KEY"
ENDPOINT = "S3_ENDPOINT_URL"


def _value(mapping: dict[str, Any], name: str) -> str | None:
    """Return the variable's value, or None when unset or empty.

    An exported-but-empty variable is a common .env artifact and must read as
    absent rather than as a credential.
    """
    value = mapping.get(name)
    return str(value) if value else None


SHELL_NAMES = (ACCESS_KEY, SECRET_KEY, ENDPOINT)


def shell_exports(creds: dict[str, str]) -> list[str]:
    """Lines for ``eval "$(get_minio_creds.py --shell)"``.

    Values go through :func:`shlex.quote` rather than being wrapped in literal
    single quotes. A secret containing a quote, a newline, or a ``$`` would
    otherwise produce a broken line at best and an injection at worst, and the
    caller is an ``eval``.

    Only the S3_* names are exported. ``scripts/configure_mc.sh`` reads those, and
    the MINIO_* spelling no longer exists on any pod.
    """
    lines: list[str] = []
    for name in SHELL_NAMES:
        lines.append(f"export {name}={shlex.quote(creds[name])}")
    lines.append(f"# source={creds['source']}")
    return lines


def _searched() -> str:
    """The variable names a failure looked for, per role, for error messages.

    Split by role rather than run together: only the access and secret keys can
    cause the failure, while the endpoint has a default and never does.
    """
    return (
        f"    access key: {ACCESS_KEY}\n"
        f"    secret key: {SECRET_KEY}\n"
        f"    endpoint (optional, defaults to {DEFAULT_ENDPOINT_URL}): {ENDPOINT}"
    )


def resolve_from_local_env() -> dict[str, str] | None:
    env = dict(os.environ)
    access_key = _value(env, ACCESS_KEY)
    secret_key = _value(env, SECRET_KEY)
    endpoint_url = _value(env, ENDPOINT) or DEFAULT_ENDPOINT_URL
    if access_key and secret_key:
        return {
            "S3_ACCESS_KEY": access_key,
            "S3_SECRET_KEY": secret_key,
            "S3_ENDPOINT_URL": endpoint_url,
            "source": "local-env",
        }
    return None


def resolve_from_berdl_remote(bootstrap_remote: bool) -> dict[str, str] | None:
    if shutil.which("berdl-remote") is None:
        return None

    if bootstrap_remote:
        login_result = run(["berdl-remote", "login"])
        if login_result.returncode != 0:
            print(login_result.stderr.strip(), file=sys.stderr)
            return None
        spawn_result = run(["berdl-remote", "spawn"])
        if spawn_result.returncode != 0:
            print(spawn_result.stderr.strip(), file=sys.stderr)
            return None

    # Ask the pod for both spellings and decide here, so the precedence rule lives
    # in one place rather than being duplicated into a remote one-liner.
    wanted = list(SHELL_NAMES)
    code = (
        "import json, os; "
        f"print(json.dumps({{n: os.getenv(n) for n in {wanted!r}}}))"
    )
    result = run(["berdl-remote", "python", code])
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        return None

    payload = parse_remote_json(result.stdout)
    if not payload:
        return None

    access_key = _value(payload, ACCESS_KEY)
    secret_key = _value(payload, SECRET_KEY)
    endpoint_url = _value(payload, ENDPOINT) or DEFAULT_ENDPOINT_URL
    if not access_key or not secret_key:
        return None

    return {
        "S3_ACCESS_KEY": access_key,
        "S3_SECRET_KEY": secret_key,
        "S3_ENDPOINT_URL": endpoint_url,
        "source": "berdl-remote",
    }


def main() -> int:
    args = parse_args()
    load_env_file(Path(args.env_file))

    creds = resolve_from_local_env()
    if creds is None:
        creds = resolve_from_berdl_remote(args.bootstrap_remote)

    if creds is None:
        print(
            "Could not resolve object-store credentials.\n"
            "  Variables looked for:\n"
            f"{_searched()}\n"
            f"  Sources tried: {args.env_file}, the local environment, "
            "and berdl-remote.\n"
            "  On a BERDL pod the current names are S3_ACCESS_KEY and S3_SECRET_KEY; "
            "MINIO_* no longer exists there.\n"
            "  This is a missing variable, not a rejected credential.",
            file=sys.stderr,
        )
        return 1

    if args.shell:
        print("\n".join(shell_exports(creds)))
    else:
        print(json.dumps(creds, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
