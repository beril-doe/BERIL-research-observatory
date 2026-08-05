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
    """Shape of the persisted auth blob.

    ``ov_url`` / ``ov_user_key`` cache the user's OpenViking credential so a
    single ``beril login`` links both BERIL and OpenViking. They are optional:
    an old auth.json predating them, or a login where OpenViking couldn't be
    reached, reads as logged-in-but-OV-unlinked (both None).
    """
    token: str
    base_url: str
    orcid_id: str
    display_name: str | None
    ov_url: str | None = None
    ov_user_key: str | None = None


def save(
    *,
    token: str,
    base_url: str,
    orcid_id: str,
    display_name: str | None,
    ov_url: str | None = None,
    ov_user_key: str | None = None,
) -> None:
    """Write auth.json with mode 0600 (POSIX).

    Uses os.open with O_CREAT | O_WRONLY | O_TRUNC so the mode is set at
    creation time — a Path.write_text + chmod dance would briefly expose
    a 0644 file to any process racing us.

    ``ov_url`` / ``ov_user_key`` are the cached OpenViking credential; pass
    both when a login (or ``beril ov setup``) successfully links OpenViking,
    or leave them None to record a BERIL-only login.
    """
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    payload: AuthRecord = AuthRecord(
        token=token,
        base_url=base_url,
        orcid_id = orcid_id,
        display_name=display_name,
        ov_url=ov_url,
        ov_user_key=ov_user_key,
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
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    # display_name is optional; everything else is required. Pulling the
    # fields explicitly (rather than AuthRecord(**raw)) means an old or
    # hand-edited file with extra/missing keys reads as "corrupt -> None"
    # or backfills display_name, instead of raising TypeError.
    try:
        data = AuthRecord(
            token=raw["token"],
            base_url=raw["base_url"],
            orcid_id=raw["orcid_id"],
            display_name=raw.get("display_name"),
            # Optional — absent in older files or a BERIL-only login.
            ov_url=raw.get("ov_url"),
            ov_user_key=raw.get("ov_user_key"),
        )
    except KeyError:
        return None
    # Minimal shape check — enough to keep type-narrowed downstream code honest.
    for key in ("token", "base_url", "orcid_id"):
        if not getattr(data, key):
            return None
    return data


def load_ov() -> tuple[str, str] | None:
    """Return the cached ``(ov_url, ov_user_key)``, or None if not linked.

    Convenience for consumers (the query CLI, ``beril ov``) that only need
    the OpenViking credential. Returns None when not logged in or when the
    login didn't link OpenViking (either field missing).
    """
    record = load()
    if record is None or not record.ov_url or not record.ov_user_key:
        return None
    return (record.ov_url, record.ov_user_key)


def clear() -> None:
    """Remove auth.json if present. Idempotent."""
    try:
        AUTH_PATH.unlink()
    except FileNotFoundError:
        pass
