"""Persistent CLI auth token store at ~/.beril/auth.json.

Stores the raw personal access token, the base URL it was minted against,
and enough identity metadata (ORCiD, display name) to render `beril auth
status` without a network call. The file is written with mode 0600 on
POSIX so other users on a shared machine can not read it. On Windows,
permissions are less strict but the file is still written.

We deliberately keep this module stdlib-only — `beril-cli` has no runtime
dependencies and we should not add one just to hold a JSON blob.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path

AUTH_DIR = Path.home() / ".beril"
AUTH_PATH = AUTH_DIR / "auth.json"


@dataclass
class AuthRecord:
    """Shape of the persisted auth blob."""
    token: str
    base_url: str
    orcid_id: str
    display_name: str | None


def save(
    *,
    token: str,
    base_url: str,
    orcid_id: str,
    display_name: str | None,
) -> None:
    """Write auth.json with mode 0600 (POSIX).

    Uses os.open with O_CREAT | O_WRONLY | O_TRUNC so the mode is set at
    creation time — a Path.write_text + chmod dance would briefly expose
    a 0644 file to any process racing us.
    """
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    payload: AuthRecord = AuthRecord(
        token=token,
        base_url=base_url,
        orcid_id = orcid_id,
        display_name=display_name
    )
    # 0o600 on POSIX; ignored (no-op) on Windows. This intentionally
    # replaces any existing file.
    fd = os.open(AUTH_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(asdict(payload), f, indent=2)
            f.write("\n")
    except BaseException:
        # If write fails partway, remove the possibly-partial file rather
        # than leaving a broken auth.json behind.
        try:
            AUTH_PATH.unlink()
        except FileNotFoundError:
            pass
        raise


def load() -> AuthRecord | None:
    """Return the persisted auth record, or None if not present.

    A corrupt file (unparseable JSON, missing required fields) also
    returns None — the caller should treat it as "not logged in" and
    the user can re-run `beril auth login`.
    """
    if not AUTH_PATH.exists():
        return None
    try:
        with AUTH_PATH.open("r") as f:
            data = AuthRecord(**json.load(f))
    except (OSError, json.JSONDecodeError):
        return None
    # Minimal shape check — enough to keep type-narrowed downstream code honest.
    for key in ("token", "base_url", "orcid_id"):
        if not getattr(data, key):
            return None
    return data


def clear() -> None:
    """Remove auth.json if present. Idempotent."""
    try:
        AUTH_PATH.unlink()
    except FileNotFoundError:
        pass
