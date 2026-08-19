"""beril start — launch a coding agent."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from beril_cli.config import get_default_agent, get_vertex_config
from beril_cli.detect import print_jupyterhub_path_hint

GITHUB_API_TIMEOUT_SECONDS = 10

#: Where omp is told to keep session transcripts: under $HOME, one directory per checkout.
#:
#: Not inside the checkout, for two reasons and the first is BERIL's own deployment. BERDL
#: compute nodes are ephemeral pods (PROJECT.md) while ``$HOME`` persists -- `beril setup`
#: says so itself -- so a transcript in the working tree is the copy that does not survive a
#: pod restart, and one under $HOME is the copy that does. Second, a session transcript is
#: the entire conversation including whatever the agent read, which is a different privacy
#: weight from `projects/*/runtime.json`; keeping it out of a public repo's tree means it
#: cannot be reached by an ignore rule drifting, a `git add -f`, or a Docker build context.
OMP_SESSION_ROOT = Path.home() / ".beril" / "omp-sessions"


def omp_session_dir(repo_root: Path) -> Path:
    """The session directory for one checkout, stable across runs and unique to it.

    Keyed by the resolved path, not the directory name: two clones both called
    ``BERIL-research-observatory`` are different checkouts whose sessions must not mix. The
    name is kept as a prefix so the directory is still recognisable to a person listing it.
    """
    resolved = Path(repo_root).resolve()
    digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:8]
    return OMP_SESSION_ROOT / f"{resolved.name}-{digest}"


def _sync_auth_token(env_path: Path) -> None:
    """Sync KBASE_AUTH_TOKEN from live environment into .env if available."""
    token = os.environ.get("KBASE_AUTH_TOKEN", "")
    if not token or not env_path.exists():
        return
    lines = env_path.read_text().splitlines()
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith("KBASE_AUTH_TOKEN="):
            if line.strip() != f"KBASE_AUTH_TOKEN={token}":
                lines[i] = f"KBASE_AUTH_TOKEN={token}"
                updated = True
            break
    else:
        lines.append(f"KBASE_AUTH_TOKEN={token}")
        updated = True
    if updated:
        env_path.write_text("\n".join(lines) + "\n")
        print("Refreshed KBASE_AUTH_TOKEN in .env")


def _find_repo_root() -> Path | None:
    """Walk up from cwd looking for PROJECT.md (repo marker)."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "PROJECT.md").exists():
            return parent
    return None


def _github_repo_slug(repo_root: Path) -> str | None:
    """Return 'owner/repo' parsed from origin's URL, or None if it isn't a GitHub remote."""
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repo_root, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    # Handles https://github.com/owner/repo(.git) and git@github.com:owner/repo(.git)
    match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def _latest_release_tag(repo_root: Path) -> str | None:
    """Return the tag of the latest published GitHub release, or None.

    Uses the public Releases API, which excludes drafts and prereleases. Raw git tags
    that were never published as a release (e.g. internal version bumps) are ignored.
    """
    slug = _github_repo_slug(repo_root)
    if not slug:
        return None
    url = f"https://api.github.com/repos/{slug}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=GITHUB_API_TIMEOUT_SECONDS) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: could not query GitHub releases: {exc}", file=sys.stderr)
        return None
    tag = payload.get("tag_name")
    return tag if isinstance(tag, str) and tag else None


def _checkout_release(repo_root: Path, requested_version: str | None) -> int:
    """Fetch tags and check out the requested release (or the latest if unspecified).

    Returns 0 on success, non-zero on failure.
    """
    fetch = subprocess.run(
        ["git", "fetch", "--tags", "--quiet"],
        cwd=repo_root, capture_output=True, text=True, check=False,
    )
    if fetch.returncode != 0:
        print(
            f"Warning: git fetch --tags failed: {fetch.stderr.strip()}",
            file=sys.stderr,
        )

    if requested_version:
        tag = requested_version if requested_version.startswith("v") else f"v{requested_version}"
        verify = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/tags/{tag}"],
            cwd=repo_root, capture_output=True, text=True, check=False,
        )
        if verify.returncode != 0:
            print(f"Error: release '{tag}' not found.", file=sys.stderr)
            return 1
    else:
        tag = _latest_release_tag(repo_root)
        if not tag:
            print("Error: no release tags found in repository.", file=sys.stderr)
            return 1

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root, capture_output=True, text=True, check=False,
    )
    target = subprocess.run(
        ["git", "rev-parse", f"{tag}^{{commit}}"],
        cwd=repo_root, capture_output=True, text=True, check=False,
    )
    if (
        head.returncode == 0
        and target.returncode == 0
        and head.stdout.strip() == target.stdout.strip()
    ):
        print(f"Already on release {tag}")
        return 0

    checkout = subprocess.run(
        ["git", "checkout", "--quiet", tag],
        cwd=repo_root, capture_output=True, text=True, check=False,
    )
    if checkout.returncode != 0:
        print(
            f"Error: failed to check out release {tag}: {checkout.stderr.strip()}",
            file=sys.stderr,
        )
        print(
            "You may have local changes. Commit or stash them and try again.",
            file=sys.stderr,
        )
        return checkout.returncode
    print(f"Checked out release {tag}")
    return 0


def _has_flag(extra_args: list[str], name: str) -> bool:
    """Whether the caller already passed ``name``, in either form.

    Both ``--flag value`` and ``--flag=value`` count. Plain membership misses the
    second, and re-adding a default the caller already set hands the agent the same
    flag twice with two different values.
    """
    return any(arg == name or arg.startswith(f"{name}=") for arg in extra_args)


def claude_defaults(agent: str, extra_args: list[str]) -> list[str]:
    """Default flags for Claude: Opus with the 1M context window, auto permissions.

    Returns nothing for other agents, and skips any flag the caller already set.
    """
    if agent != "claude":
        return []
    flags: list[str] = []
    if not _has_flag(extra_args, "--model"):
        flags += ["--model", "opus[1m]"]
    if not _has_flag(extra_args, "--permission-mode"):
        flags += ["--permission-mode", "auto"]
    return flags


def omp_defaults(agent: str, extra_args: list[str], repo_root: Path) -> list[str]:
    """Default flags for omp: a session directory inside the checkout.

    Returns nothing for other agents, and skips the flag if the caller already set it.

    omp writes its transcript to ``~/.omp/agent/sessions/<encoded-cwd>/`` under a name
    it picks -- a timestamp and a UUID -- so the path is knowable only after the fact.
    Because ``beril start`` launches from the repo root, every project on a machine
    also shares one such directory. Nothing downstream can name a session file, and
    naming one is exactly what a transcript reader needs: evalome's ``collect`` takes
    ``--transcript <path>``, and unlike Claude Code, omp fires no SessionStart hook to
    supply it.

    Pointing omp at the checkout fixes the directory without inventing the filename.
    The newest ``.jsonl`` under it is the session just launched, printed at launch so
    the operator can hand it straight to a collector.

    Repo-root, not per-project: ``/berdl_start`` scaffolds the project *during* the
    session, so at launch there is no project directory to write into yet.
    """
    if agent != "omp" or _has_flag(extra_args, "--session-dir"):
        return []
    return ["--session-dir", str(omp_session_dir(repo_root))]


def announce_omp_session(session_flags: list[str]) -> None:
    """Tell the operator where the transcript will land. A no-op for any other agent.

    Deliberately does not create the directory. omp creates it itself, recursively, when it
    opens the session -- verified against the shipped binary -- so a `mkdir` here buys
    nothing and can only fail. It would run *between* "Launching omp..." and `execvp`, where
    a path occupied by a file, a read-only mount or a full disk raises and the agent never
    starts, having told the operator it was starting.
    """
    if not session_flags:
        return
    print(f"omp transcripts: {session_flags[1]} (this session is the newest *.jsonl)")


def run_start(
    agent: str | None = None,
    extra_args: list[str] | None = None,
    skip_onboard: bool = False,
    version: str | None = None,
    dev_mode: bool = False
) -> int:
    """Launch the selected coding agent from the repo root."""
    agent = agent or get_default_agent()
    extra_args = extra_args or []

    binary = shutil.which(agent)
    if not binary:
        print(f"Error: '{agent}' is not installed or not on PATH.", file=sys.stderr)
        print("Install it and try again, or choose a different agent with --agent.", file=sys.stderr)
        return 1

    # Ensure we launch from the repo root so agent workflows have correct paths
    repo_root = _find_repo_root()
    if repo_root:
        os.chdir(repo_root)
    else:
        print("Error: BERIL repository not found. Run 'beril setup' first.", file=sys.stderr)
        return 1

    # Check out the requested release (or the latest published tag by default).
    if not dev_mode:
        rc = _checkout_release(repo_root, version)
        if rc != 0:
            return rc

    # Refresh KBASE_AUTH_TOKEN in .env from live environment (tokens expire)
    _sync_auth_token(repo_root / ".env")

    # Auto-run the onboarding skill unless skipped or the user already passed a prompt
    if not skip_onboard and not extra_args:
        extra_args = ["/berdl_start"]

    # Configure Google Vertex if enabled (shared BERIL Anthropic key)
    if agent == "claude":
        vertex = get_vertex_config()
        if vertex.get("enabled"):
            creds = vertex.get("credentials_file", "")
            if creds and Path(creds).exists():
                os.environ["CLAUDE_CODE_USE_VERTEX"] = "1"
                os.environ["CLOUD_ML_REGION"] = vertex.get("region", "global")
                os.environ["ANTHROPIC_VERTEX_PROJECT_ID"] = vertex.get("project_id", "")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds
                os.environ["VERTEX_REGION_CLAUDE_HAIKU_4_5"] = "us-east5"
                os.environ["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = "claude-haiku-4-5@20251001"
                print("Using BERIL Anthropic key (Google Vertex)")
            else:
                print(
                    "Warning: Vertex enabled but credentials file not found. "
                    "Falling back to personal API key.",
                    file=sys.stderr,
                )

    # Computed from the operator's own args, so this runs after the onboarding default
    # above and never itself counts as "the user already passed a prompt".
    session_flags = omp_defaults(agent, extra_args, repo_root)
    extra_args = [*claude_defaults(agent, extra_args), *session_flags, *extra_args]

    print(f"Launching {agent}...")
    announce_omp_session(session_flags)
    print_jupyterhub_path_hint(repo_root)
    # Replace the current process with the agent
    os.execvp(binary, [agent, *extra_args])

    # execvp doesn't return on success; this is only reached on failure
    return 1  # pragma: no cover
