"""beril auth — log in / show status / log out of a BERIL server.

login flow:
  1. If --base-url is given, use and persist it (so future runs don't
     need it). Otherwise resolve from config or the compiled-in default.
  2. If --token is given, use it directly (scriptable / headless path).
     Otherwise print the "open <url>/account/tokens in a browser and
     paste the token" prompt and read via getpass so the token does not
     echo on the terminal.
  3. GET /api/user/whoami with Authorization: Bearer <token>. If 2xx,
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

import getpass
import json
import sys

import httpx

from beril_cli import auth_store, config
from beril_cli.ov_client import OvLinkError, fetch_ov_credential

_WHOAMI_PATH = "/api/user/whoami"
_HTTP_TIMEOUT_SECONDS = 15.0

# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


def run_login(token: str|None = None, base_url: str|None = None, status:bool=False) -> int:
    """
    Performs the action that lets a user log in to the BERIL webapp
    locally.

    arg options:
    base_url: if not None, set the base url for the BERIL server (i.e. https://beril.kbase.us)
      this happens BEFORE any other action takes place, including login and status checking
    token: if not None, this skips the token prompt and uses the given token
    status: if True, this does no login change (i.e. setting the token) and returns
      the current token status. If a token is not currently set, it prints an error
      and returns 1.
    """

    if base_url is not None:
        config.set_base_url(base_url)
    base_url = config.get_base_url()

    if status:
        return check_status()

    if token is None:
        token = ""
    token = token.strip()
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

    # Link OpenViking in the same step. This is best-effort: a valid BERIL
    # login must still succeed (and be saved) even if OpenViking is
    # unreachable or the 409 "key exists but BERIL holds none" case fires —
    # the user can repair it later with `beril ov setup [--regenerate]`.
    ov_url: str | None = None
    ov_user_key: str | None = None
    ov_warning: str | None = None
    try:
        ov_url, ov_user_key = fetch_ov_credential(base_url, token)
    except OvLinkError as e:
        if e.needs_regenerate:
            ov_warning = (
                f"OpenViking not linked: {e} "
                "Run `beril ov setup --regenerate` to mint a fresh key."
            )
        else:
            ov_warning = (
                f"OpenViking not linked: {e} "
                "Run `beril ov setup` to link it later."
            )

    auth_store.save(
        token=token,
        base_url=base_url,
        orcid_id=identity["orcid_id"],
        display_name=identity.get("display_name"),
        ov_url=ov_url,
        ov_user_key=ov_user_key,
    )
    name = identity.get("display_name") or identity["orcid_id"]
    print(f"Logged in to {base_url} as {name} ({identity['orcid_id']}).")
    if not ov_user_key:
        print(ov_warning, file=sys.stderr)
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

def check_status() -> int:
    record = auth_store.load()
    if record is None:
        print("Not logged in. Run `beril login` to authenticate.")
        return 1

    # validate token
    try:
        _whoami(record.base_url, record.token)
    except _WhoamiError as e:
        if e.rejected:
            print(
                f"Stored credentials are no longer valid: {e}\n"
                "Run `beril login` to re-authenticate, or "
                "`beril logout` to remove them.",
                file=sys.stderr
            )
            return 1
        elif e.unreachable:
            print(
                f"Could not verify credentials: {e}\n"
                "Your stored login may still be valid, the server was unreachable",
                file=sys.stderr
            )
            return 2
        else:
            print(
                f"An error occurred while checking your stored login credentials: {e}",
                file=sys.stderr,
            )
            return 2

    name = record.display_name or record.orcid_id
    print(f"Logged in as {name} ({record.orcid_id}) on {record.base_url}.")
    print(f"Token file: {auth_store.AUTH_PATH}")
    return 0


# ---------------------------------------------------------------------------
# logout
# ---------------------------------------------------------------------------


def run_logout() -> int:
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
    def __init__(self, msg: str, rejected:bool=False, unreachable: bool=False):
        super().__init__(msg)
        self.rejected = rejected
        self.unreachable = unreachable


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
        raise _WhoamiError(f"timed out talking to {base_url}.", unreachable=True) from e
    except httpx.TransportError as e:
        # Covers ConnectError, ReadError, WriteError, ProtocolError, etc.
        raise _WhoamiError(f"could not reach {base_url}: {e}", unreachable=True) from e

    if res.status_code == 401:
        raise _WhoamiError("token was rejected by the server (401).", rejected=True)
    if res.status_code == 403:
        raise _WhoamiError("unable to retrieve information with this token (403).", rejected=True)
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
