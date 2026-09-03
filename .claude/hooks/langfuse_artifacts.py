#!/usr/bin/env python3
"""SessionEnd hook → upload the session's project artifacts to Langfuse.

Resolves the BERIL project the session bound to (runtime.json, via
beril_cli.project_resolution) and attaches REPORT.md / RESEARCH_PLAN.md /
WORKLOG.md as media on a span carrying the session_id, so the files land next
to the session's conversation traces. Strictly best-effort: always exits 0.

Also the single home of get_user_id(), imported by langfuse_hook.py so both
hooks attribute to the same identity.

Failures are logged to ~/.claude/state/langfuse_artifacts.log.
"""

import json
import os
import subprocess
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


@lru_cache(maxsize=1)
def get_user_id() -> str | None:
    """LANGFUSE_USER_ID > git user.email > $USER — one rule for both hooks."""
    uid = os.environ.get("LANGFUSE_USER_ID", "").strip()
    if not uid:
        try:
            r = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True, text=True, timeout=5, cwd=REPO_ROOT,
            )
            uid = r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            uid = ""
    return uid or os.environ.get("USER") or None


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
    # Same credential resolution as langfuse_hook.py: CC_-prefixed names win.
    public_key = os.environ.get("CC_LANGFUSE_PUBLIC_KEY") or os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("CC_LANGFUSE_SECRET_KEY") or os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("CC_LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
    if not public_key or not secret_key:
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
    try:
        from langfuse import Langfuse, propagate_attributes
        from langfuse.media import LangfuseMedia

        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
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
