#!/usr/bin/env python3
"""SessionEnd hook → upload the session's project artifacts to Langfuse.

Resolves the BERIL project the session bound to (runtime.json, via
beril_cli.project_resolution) and attaches REPORT.md / RESEARCH_PLAN.md /
WORKLOG.md as media on a span carrying the session_id, so the files land next
to the session's conversation traces. Strictly best-effort: always exits 0.

Also the single home of get_user_id() and relay_client_kwargs(), imported by
langfuse_hook.py so both hooks attribute to the same identity and reach
Langfuse the same way: through the BERIL relay (ui/app/routes/langfuse.py),
authenticated with the `beril login` token. No Langfuse keys on this machine.

Failures are logged to ~/.claude/state/langfuse_artifacts.log.
"""

import json
import logging
import os
import re
import sys
import threading
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

ARTIFACTS = ("REPORT.md", "RESEARCH_PLAN.md", "WORKLOG.md")
# .absolute(), not .resolve(): a symlinked hook must act on the tree it is
# linked into, not where the file really lives (same rule as dash_stop.py).
REPO_ROOT = Path(__file__).absolute().parent.parent.parent
LOG_FILE = Path.home() / ".claude" / "state" / "langfuse_artifacts.log"

sys.path.insert(0, str(REPO_ROOT))


def log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"{stamp} {msg}\n")
    except Exception:
        pass


# Traces carry every tool output, so anything a session `cat`s lands in the
# shared project; live credentials have done exactly that before
# (langfuse-retro-load#4). The SDK applies this to every observation's
# input/output/metadata before export. Best-effort by nature: a bare token
# with no surrounding context can't be recognised, so docs/langfuse.md still
# says not to trace sessions handling data that must not leave the machine.
# Group 1, when present, is the prefix to keep; the rest is the secret.
_SECRET_PATTERNS = [
    re.compile(r"beril_[0-9a-f]{48}"),                              # BERIL PAT
    re.compile(r"\b[ps]k-lf-[0-9a-f-]{20,}"),                        # Langfuse keys
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                             # AWS access key id
    re.compile(r"\beyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}"),           # JWT
    re.compile(r"(?i)(authorization\s*[:=]\s*(?:bearer|basic|token)\s+)\S+"),
    re.compile(r"(?i)(-u\s+['\"]?)[^\s'\"]+:[^\s'\"]+"),               # curl -u user:pass
    re.compile(
        r"(?i)((?:token|secret|password|passwd|credential|api[_-]?key|access[_-]?key"
        r"|secret[_-]?key|user[_-]?key|private[_-]?key)\w*[\"']?\s*[=:]\s*[\"']?)"
        r"[^\s\"',;&]+"
    ),
]
_REDACTED = "[REDACTED]"


def _sub(m: re.Match) -> str:
    return (m.group(1) if m.lastindex else "") + _REDACTED


def redact(data=None, **_):
    """Langfuse `mask` hook: scrub credential-shaped strings, recursively."""
    if isinstance(data, str):
        for pat in _SECRET_PATTERNS:
            data = pat.sub(_sub, data)
        return data
    if isinstance(data, dict):
        return {k: redact(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return type(data)(redact(v) for v in data)
    return data


class _SdkLogHandler(logging.Handler):
    """Forward SDK/exporter warnings into this hook's log file."""

    def emit(self, record: logging.LogRecord) -> None:
        log(f"[{record.name}] {record.getMessage()}")


def route_sdk_logs() -> None:
    """Export failures are logged by the SDK, never raised, and the detached
    hook's stderr is /dev/null — without this a dropped upload leaves no trace.
    """
    for name in ("langfuse", "opentelemetry.exporter.otlp.proto.http.trace_exporter"):
        lg = logging.getLogger(name)
        lg.setLevel(logging.WARNING)
        lg.addHandler(_SdkLogHandler(level=logging.WARNING))


@lru_cache(maxsize=1)
def _login():
    """The `beril login` record, or None (not logged in / unreadable / no CLI)."""
    try:
        from beril_cli.auth_store import load

        return load()
    except Exception as e:
        log(f"login record unavailable: {type(e).__name__}: {e}")
        return None


@lru_cache(maxsize=1)
def get_user_id() -> str | None:
    """LANGFUSE_USER_ID > ORCiD from `beril login` — one rule for both hooks."""
    uid = os.environ.get("LANGFUSE_USER_ID", "").strip()
    if uid:
        return uid
    rec = _login()
    return rec.orcid_id if rec else None


def relay_client_kwargs() -> dict | None:
    """Langfuse() kwargs that route through the BERIL relay, or None if not logged in.

    The SDK only speaks Basic auth, so the BERIL personal access token rides
    as the password; the relay validates it and swaps in the server-held
    project keypair. The custom User-Agent matters: Cloudflare in front of the
    prod server 403s some default Python UAs (see beril_cli.auth_cmd).

    ``base_url`` (not ``host``): the SDK resolves base_url > $LANGFUSE_BASE_URL
    > host, so with ``host`` a stale LANGFUSE_BASE_URL in .env would send the
    BERIL token to Langfuse Cloud instead of the relay.
    """
    rec = _login()
    if rec is None:
        return None
    return {
        "public_key": "beril",
        "secret_key": rec.token,
        "base_url": rec.base_url.rstrip("/") + "/lf",
        "additional_headers": {"User-Agent": "beril-langfuse-hook"},
        "mask": redact,
    }


def find_uploads(session_id: str, repo_root: Path) -> tuple[str, list[Path]] | None:
    """(project, existing artifact files) for the session, or None."""
    from beril_cli.project_resolution import project_from_runtime

    project = project_from_runtime(session_id, repo_root)
    if not project:
        return None
    project_dir = repo_root / "projects" / project
    files = [p for name in ARTIFACTS if (p := project_dir / name).is_file()]
    return (project, files) if files else None


def main() -> int:
    if os.environ.get("TRACE_TO_LANGFUSE") != "true":
        return 0
    client_kwargs = relay_client_kwargs()
    if not client_kwargs:
        return 0

    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    session_id = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not isinstance(session_id, str) or not session_id:
        return 0

    try:
        found = find_uploads(session_id, REPO_ROOT)
    except Exception as e:
        log(f"resolution failed: {type(e).__name__}: {e}")
        return 0
    if not found:
        return 0
    project, files = found

    langfuse = None
    route_sdk_logs()
    try:
        from langfuse import Langfuse, propagate_attributes
        from langfuse.media import LangfuseMedia

        langfuse = Langfuse(**client_kwargs)
        media = {
            p.name: LangfuseMedia(content_bytes=p.read_bytes(), content_type="text/markdown")
            for p in files
        }
        prop: dict = {"session_id": session_id, "tags": ["beril", "artifacts", project]}
        uid = get_user_id()
        if uid:
            prop["user_id"] = uid
        with propagate_attributes(**prop):
            span = langfuse.start_observation(
                name=f"BERIL artifacts — {project}",
                as_type="span",
                input={"project": project, "files": [p.name for p in files]},
                metadata=media,
            )
            span.end()
        log(f"uploaded {[p.name for p in files]} for {project} (session={session_id})")
    except Exception as e:
        log(f"upload failed: {type(e).__name__}: {e}")
    finally:
        if langfuse is not None:
            # shutdown() flushes; daemon thread + join cap so an unreachable
            # Langfuse can't stall session exit.
            t = threading.Thread(target=langfuse.shutdown, daemon=True)
            t.start()
            t.join(10.0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
