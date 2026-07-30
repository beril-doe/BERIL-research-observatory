"""beril doctor — environment health check."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import httpx

from beril_cli import auth_store, config

# Public, unauthenticated health endpoints. `/health` is the BERIL webapp's own
# check; `/ov/health` is the nginx proxy path that forwards to OpenViking's
# `/health` (the "context manager" users interact with).
_HEALTH_PATH = "/health"
_OV_HEALTH_PATH = "/ov/health"
_HTTP_TIMEOUT_SECONDS = 10.0


def _find_repo_root() -> Path | None:
    """Walk up from cwd looking for PROJECT.md (repo marker)."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "PROJECT.md").exists():
            return parent
    return None


def _parse_env_file(env_path: Path) -> dict[str, str]:
    """Minimal .env parser — returns key-value pairs."""
    env_vars: dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            env_vars[key] = value
    return env_vars


def _run_silent(cmd: list[str], timeout: int = 10, env: dict | None = None) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False,
            env=env,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"{cmd[0]}: command not found"
    except subprocess.TimeoutExpired:
        return -1, "", f"{cmd[0]}: timed out"


def _get_health(url: str) -> tuple[int | None, dict | None, str]:
    """GET a public health endpoint. Returns (status_code, json_body, error).

    ``status_code`` is None and ``error`` is populated when the server could
    not be reached at all (DNS, connection, timeout). Otherwise ``status_code``
    is the HTTP status and ``error`` is empty; ``json_body`` is the parsed body
    when the response was JSON, else None.
    """
    try:
        resp = httpx.get(url, timeout=_HTTP_TIMEOUT_SECONDS)
    except httpx.TimeoutException:
        return None, None, "timed out"
    except httpx.HTTPError as exc:
        return None, None, str(exc) or exc.__class__.__name__
    try:
        body = resp.json()
    except ValueError:
        body = None
    return resp.status_code, body if isinstance(body, dict) else None, ""


def _check_beril_login() -> tuple[str, str]:
    """Return (status, detail) describing the stored BERIL login."""
    record = auth_store.load()
    if record is None:
        return "WARN", "not logged in — run `beril login`"

    name = record.display_name or record.orcid_id
    # Validate the stored token so an expired/revoked login is caught, not just
    # reported as "logged in" from a stale file.
    url = record.base_url.rstrip("/") + "/api/user/whoami"
    try:
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {record.token}"},
            timeout=_HTTP_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError:
        # Can't reach the server to validate — the login may still be fine.
        return "WARN", f"{name} (stored token; server unreachable to verify)"

    if resp.status_code in (401, 403):
        return "FAIL", f"stored token rejected ({resp.status_code}) — run `beril login`"
    if resp.status_code >= 400:
        return "WARN", f"{name} (could not verify token: HTTP {resp.status_code})"
    return "PASS", f"{name} ({record.orcid_id})"


def _check_beril_webapp(base_url: str) -> tuple[str, str]:
    """Return (status, detail) for the BERIL webapp's public /health endpoint."""
    code, body, error = _get_health(base_url + _HEALTH_PATH)
    if code is None:
        return "FAIL", f"unreachable at {base_url} ({error})"
    if code != 200:
        return "FAIL", f"HTTP {code} from {base_url}{_HEALTH_PATH}"
    health = (body or {}).get("status")
    if health == "healthy":
        return "PASS", f"healthy ({base_url})"
    if health:
        # e.g. "degraded" — reachable but a subservice (like the DB) is down.
        return "WARN", f"{health} ({base_url})"
    return "PASS", f"reachable ({base_url})"


def _check_context_manager(base_url: str) -> tuple[str, str]:
    """Return (status, detail) for OpenViking (the "context manager") via /ov/health."""
    code, body, error = _get_health(base_url + _OV_HEALTH_PATH)
    if code is None:
        return "FAIL", f"unreachable ({error})"
    if code != 200:
        return "FAIL", f"HTTP {code} from {base_url}{_OV_HEALTH_PATH}"
    status = (body or {}).get("status")
    if status in ("ok", "healthy", None):
        return "PASS", f"reachable ({base_url}{_OV_HEALTH_PATH})"
    return "WARN", f"{status} ({base_url}{_OV_HEALTH_PATH})"


def run_doctor() -> int:
    """Run all environment checks and print a status table."""
    checks: list[tuple[str, str, str]] = []  # (label, status, detail)
    has_critical_failure = False

    # 1. Repo root
    repo_root = _find_repo_root()
    if repo_root:
        checks.append(("Repo root", "PASS", str(repo_root)))
    else:
        checks.append(("Repo root", "FAIL", "PROJECT.md not found in any parent directory"))
        has_critical_failure = True

    # 2. Python
    rc, stdout, _ = _run_silent([sys.executable, "--version"])
    if rc == 0:
        checks.append(("Python", "PASS", stdout.strip()))
    else:
        checks.append(("Python", "FAIL", "python3 not available"))
        has_critical_failure = True

    # 3. Git
    rc, stdout, _ = _run_silent(["git", "--version"])
    if rc == 0:
        checks.append(("Git", "PASS", stdout.strip()))
    else:
        checks.append(("Git", "FAIL", "git not available"))
        has_critical_failure = True

    # 4. gh CLI
    rc, _, stderr = _run_silent(["gh", "auth", "status"])
    if rc == 0:
        checks.append(("gh auth", "PASS", "authenticated"))
    else:
        msg = "not authenticated" if shutil.which("gh") else "gh not installed"
        checks.append(("gh auth", "WARN", msg))

    # 5. KBASE_AUTH_TOKEN — check both .env file and process environment
    env_token = os.environ.get("KBASE_AUTH_TOKEN", "")
    if repo_root:
        env_path = repo_root / ".env"
        env_vars = _parse_env_file(env_path)
        file_token = env_vars.get("KBASE_AUTH_TOKEN", "")
        if file_token and file_token != "YOUR_AUTH_TOKEN_HERE":
            checks.append(("KBASE_AUTH_TOKEN", "PASS", "present in .env"))
        elif env_token:
            checks.append(("KBASE_AUTH_TOKEN", "PASS", "present in environment"))
        elif not env_path.exists():
            checks.append(("KBASE_AUTH_TOKEN", "FAIL", ".env file missing"))
            has_critical_failure = True
        else:
            checks.append(("KBASE_AUTH_TOKEN", "FAIL", "not set in .env or environment"))
            has_critical_failure = True
    elif env_token:
        checks.append(("KBASE_AUTH_TOKEN", "PASS", "present in environment"))
    else:
        checks.append(("KBASE_AUTH_TOKEN", "FAIL", "not found in environment"))
        has_critical_failure = True

    # 6. Agent CLIs
    agents_found = []
    for agent in ("claude", "codex", "gemini"):
        if shutil.which(agent):
            agents_found.append(agent)
    if agents_found:
        checks.append(("Agent CLIs", "PASS", ", ".join(agents_found)))
    else:
        checks.append(("Agent CLIs", "WARN", "none found (claude, codex, gemini)"))

    # 7. BERIL webapp: login state + service availability. These are
    # informational (WARN, not FAIL) so a transient outage doesn't make doctor
    # exit non-zero for an otherwise-fine local setup.
    base_url = config.get_base_url()

    status, detail = _check_beril_login()
    checks.append(("BERIL login", status, detail))

    status, detail = _check_beril_webapp(base_url)
    checks.append(("BERIL webapp", status, detail))

    status, detail = _check_context_manager(base_url)
    checks.append(("Context manager", status, detail))

    # 8. BERDL environment
    if repo_root:
        detect_script = repo_root / "scripts" / "detect_berdl_environment.py"
        if detect_script.exists():
            # Pass .env values via environment so the detect script
            # sees them and doesn't try to write back to .env.
            # Doctor should be read-only.
            detect_env = os.environ.copy()
            for k, v in _parse_env_file(repo_root / ".env").items():
                detect_env.setdefault(k, v)
            rc, stdout, _ = _run_silent(
                [sys.executable, str(detect_script)], timeout=15,
                env=detect_env,
            )
            try:
                env_info = json.loads(stdout)
                location = env_info.get("location", "unknown")
                ready = env_info.get("ready", False)
                status = "PASS" if ready else "WARN"
                detail = f"{location}, {'ready' if ready else 'not ready'}"
                checks.append(("BERDL environment", status, detail))
                # Show next steps if not ready
                if not ready:
                    for step in env_info.get("next_steps", []):
                        checks.append(("", "", f"  {step}"))
            except (json.JSONDecodeError, KeyError):
                checks.append(("BERDL environment", "WARN", "detection script returned invalid output"))
        else:
            checks.append(("BERDL environment", "WARN", "detection script not found"))
    else:
        checks.append(("BERDL environment", "WARN", "cannot check without repo root"))

    # Print results
    print()
    print("BERIL Environment Check")
    print("=" * 60)
    for label, status, detail in checks:
        if not label:
            # Continuation line (e.g., next steps)
            print(f"            {detail}")
        else:
            color = {"PASS": "\033[32m", "FAIL": "\033[31m", "WARN": "\033[33m"}.get(status, "")
            reset = "\033[0m" if color else ""
            print(f"  {color}{status:4s}{reset}  {label:<20s} {detail}")
    print()

    return 1 if has_critical_failure else 0
