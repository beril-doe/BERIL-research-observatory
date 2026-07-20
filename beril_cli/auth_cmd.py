"""beril auth — log in / show status / log out of a BERIL server.

login flow:
  1. If --base-url is given, use and persist it (so future runs don't
     need it). Otherwise resolve from config or the compiled-in default.
  2. If --token is given, use it directly (scriptable / headless path).
     Otherwise print the "open <url>/account/tokens in a browser and
     paste the token" prompt and read via getpass so the token does not
     echo on the terminal.
  3. POST /api/user/whoami with Authorization: Bearer <token>. If 2xx,
     parse ORCiD + display name and save to ~/.beril/auth.json (mode
     0600). If not, print the server error and exit non-zero without
     writing anything.

status: print who the stored token belongs to. Non-zero exit if not
logged in.

logout: remove ~/.beril/auth.json. Idempotent.

Uses httpx for HTTP. urllib was tried first (to keep beril-cli
dep-free) but Cloudflare in front of the prod server rejects the
default ``Python-urllib/*`` User-Agent with a 403 while letting
``httpx``'s default UA through.
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys

import httpx

from beril_cli import auth_store, config

_WHOAMI_PATH = "/api/user/whoami"
_HTTP_TIMEOUT_SECONDS = 15.0


def run_auth(args: argparse.Namespace) -> int:
    """Dispatch on args.action (login/status/logout)."""
    action = getattr(args, "action", None)
    if action == "login":
        return _run_login(args)
    if action == "status":
        return _run_status(args)
    if action == "logout":
        return _run_logout(args)
    # argparse's `choices=` already rejects anything else, but be defensive.
    print(f"Unknown auth action: {action}", file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


def _run_login(args: argparse.Namespace) -> int:
    # Resolve and (if given) persist the base URL BEFORE reading the token
    # so a --base-url override affects the whoami request in this same
    # invocation.
    if getattr(args, "base_url", None):
        config.set_base_url(args.base_url)
    base_url = config.get_base_url()

    token = (getattr(args, "token", None) or "").strip()
    if not token:
        token = _prompt_for_token(base_url)
    if not token:
        print("No token provided.", file=sys.stderr)
        return 1

    try:
        identity = _whoami(base_url, token)
    except _WhoamiError as e:
        print(f"Login failed: {e}", file=sys.stderr)
        return 1

    auth_store.save(
        token=token,
        base_url=base_url,
        orcid_id=identity["orcid_id"],
        display_name=identity.get("display_name"),
    )
    name = identity.get("display_name") or identity["orcid_id"]
    print(f"Logged in to {base_url} as {name} ({identity['orcid_id']}).")
    return 0


def _prompt_for_token(base_url: str) -> str:
    print(
        "To log in:\n"
        f"  1. Open {base_url}/account/tokens in your browser\n"
        "  2. Create a new personal access token\n"
        "  3. Paste it below (input will not echo)\n"
    )
    try:
        return getpass.getpass("Token: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("", file=sys.stderr)  # newline so the shell prompt looks clean
        return ""


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def _run_status(args: argparse.Namespace) -> int:
    record = auth_store.load()
    if record is None:
        print("Not logged in. Run `beril auth login` to authenticate.")
        return 1

    if getattr(args, "json", False):
        # Redact the token from status output — CLI status is a human
        # convenience, not a token exporter.
        payload = {
            "base_url": record["base_url"],
            "orcid_id": record["orcid_id"],
            "display_name": record.get("display_name"),
            "path": str(auth_store.AUTH_PATH),
        }
        json.dump(payload, sys.stdout)
        sys.stdout.write("\n")
        return 0

    name = record.get("display_name") or record["orcid_id"]
    print(f"Logged in as {name} ({record['orcid_id']}) on {record['base_url']}.")
    print(f"Token file: {auth_store.AUTH_PATH}")
    return 0


# ---------------------------------------------------------------------------
# logout
# ---------------------------------------------------------------------------


def _run_logout(args: argparse.Namespace) -> int:
    had_record = auth_store.load() is not None
    auth_store.clear()
    if had_record:
        print("Logged out.")
    else:
        # Idempotent: still exit 0, but be honest that there was nothing
        # to clear so scripts can tell.
        print("Not logged in; nothing to do.")
    return 0


# ---------------------------------------------------------------------------
# whoami HTTP call
# ---------------------------------------------------------------------------


class _WhoamiError(Exception):
    """Any failure of the whoami validation call. Message is user-facing."""


def _whoami(base_url: str, token: str) -> dict:
    """Call GET {base_url}/api/user/whoami with the given Bearer token.

    Returns the parsed JSON dict on success (guaranteed to contain at
    least ``orcid_id``). Raises _WhoamiError on any failure with a
    message suitable for printing to the user.
    """
    url = base_url.rstrip("/") + _WHOAMI_PATH
    try:
        res = httpx.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=_HTTP_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException as e:
        # TimeoutException is a subclass of TransportError; catch it first
        # so timeouts get their specific message.
        raise _WhoamiError(f"timed out talking to {base_url}.") from e
    except httpx.TransportError as e:
        # Covers ConnectError, ReadError, WriteError, ProtocolError, etc.
        raise _WhoamiError(f"could not reach {base_url}: {e}") from e

    if res.status_code == 401:
        raise _WhoamiError("token was rejected by the server (401).")
    if res.status_code == 403:
        raise _WhoamiError("unable to retrieve information with this token (403).")
    if res.status_code >= 400:
        raise _WhoamiError(
            f"an error occurred while validating token at {base_url} ({res.status_code})"
        )

    try:
        data = res.json()
    except (json.JSONDecodeError, ValueError) as e:
        # res.json() raises ValueError on garbage bodies; JSONDecodeError
        # is a ValueError subclass but we spell both for clarity.
        raise _WhoamiError("server returned invalid JSON.") from e

    if not isinstance(data, dict) or "orcid_id" not in data:
        raise _WhoamiError("server response missing orcid_id.")
    return data
