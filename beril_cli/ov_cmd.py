"""beril ov — link, inspect, and export the OpenViking (OV) credential.

`beril login` already links OV in the happy path (see auth_cmd). This command
covers the cases login intentionally doesn't force:

  beril ov setup                re-link OV against the stored PAT (repair path:
                                login couldn't reach OV, or an old auth.json
                                predates OV linking).
  beril ov setup --regenerate   mint a fresh OV key (invalidates the old one) —
                                the recovery path for the 409 "key exists but
                                BERIL holds none" case, and for key rotation.
  beril ov status               show the cached OV credential and probe health.
  beril ov print-env            emit OPENVIKING_URL / OPENVIKING_API_KEY lines
                                for `.env` or `eval "$(beril ov print-env)"`.

All of these reuse the stored BERIL PAT (~/.beril/auth.json) — no browser
cookie. The credential exchange itself lives in ov_client, shared with login.
"""

from __future__ import annotations

import argparse
import sys

from beril_cli import auth_store
from beril_cli.ov_client import OvLinkError, fetch_ov_credential, ov_health


def run_ov(args: argparse.Namespace) -> int:
    action = getattr(args, "ov_action", None)
    if action == "setup":
        return _run_setup(regenerate=args.regenerate)
    if action == "status":
        return _run_status()
    if action == "print-env":
        return _run_print_env()
    # argparse is configured with required subcommands, so this is unreachable
    # in normal dispatch; guard anyway.
    print("Usage: beril ov {setup|status|print-env}", file=sys.stderr)
    return 1


def _require_login() -> auth_store.AuthRecord | None:
    record = auth_store.load()
    if record is None:
        print("Not logged in. Run `beril login` first.", file=sys.stderr)
        return None
    return record


def _run_setup(*, regenerate: bool) -> int:
    record = _require_login()
    if record is None:
        return 1

    try:
        ov_url, ov_user_key = fetch_ov_credential(
            record.base_url, record.token, regenerate=regenerate
        )
    except OvLinkError as e:
        print(f"OpenViking setup failed: {e}", file=sys.stderr)
        if e.needs_regenerate:
            print(
                "Run `beril ov setup --regenerate` to mint a fresh key.",
                file=sys.stderr,
            )
        return 1

    # Re-persist the full record so the BERIL token/identity are preserved and
    # only the OV fields change.
    auth_store.save(
        token=record.token,
        base_url=record.base_url,
        orcid_id=record.orcid_id,
        display_name=record.display_name,
        ov_url=ov_url,
        ov_user_key=ov_user_key,
    )
    verb = "regenerated" if regenerate else "linked"
    print(f"OpenViking {verb} ({_mask(ov_user_key)}). URL: {ov_url}")
    return 0


def _run_status() -> int:
    record = _require_login()
    if record is None:
        return 1

    if not record.ov_url or not record.ov_user_key:
        print("OpenViking is not linked. Run `beril ov setup` to link it.")
        # Not an error state per se, but scripts should be able to tell.
        return 1

    print(f"OpenViking URL: {record.ov_url}")
    print(f"API key:        {_mask(record.ov_user_key)}")

    # Best-effort health probe — never let it fail the command.
    try:
        body = ov_health(record.base_url, record.token)
        status = body.get("status", "unknown")
        print(f"Server health:  {status}")
    except OvLinkError as e:
        print(f"Server health:  unknown ({e})")
    return 0


def _run_print_env() -> int:
    creds = auth_store.load_ov()
    if creds is None:
        print(
            "OpenViking is not linked. Run `beril login` or `beril ov setup` first.",
            file=sys.stderr,
        )
        return 1
    ov_url, ov_user_key = creds
    print(f"OPENVIKING_URL={ov_url}")
    print(f"OPENVIKING_API_KEY={ov_user_key}")
    return 0


def _mask(secret: str) -> str:
    """Show only the last 4 chars of a secret for confirmation output."""
    return f"…{secret[-4:]}" if len(secret) > 4 else "set"
