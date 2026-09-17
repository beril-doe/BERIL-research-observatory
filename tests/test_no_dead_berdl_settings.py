"""Guard against BERDL names that a current pod no longer provides.

BERDL renamed three things on the way from ``MINIO_*`` to ``S3_*``, and each one
fails in a different way at a different moment: a missing settings attribute
raises ``AttributeError`` at call time, a renamed module and a renamed function
raise ``ImportError`` at import time.

Every one of them is invisible until the code runs on a pod, which is how eight
`data/` scripts stayed broken for months while reading fine. This test is static,
so it needs no pod, no credentials and no BERDL packages, and CI catches a
reintroduction the same day rather than the next time someone runs an ingest.

The endpoint rename alone was fixed three times before this guard existed: in
pull requests 380 (the credential resolver and skill docs), 401
(``observatory_context/config.py``) and 412 (the eight `data/` scripts). The
other two renames were only found by running the code on a pod, after 412 had
already been opened claiming the fix was complete.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Three separate renames, all of which only fail when run on a pod.
#
#  1. Attribute access on a settings object, e.g. ``settings.MINIO_ENDPOINT_URL``.
#     Deliberately not matching ``os.environ["MINIO_..."]`` or prose: an env var
#     that is merely absent falls back cleanly, a missing attribute raises.
#  2. ``berdl_notebook_utils.minio_governance``, renamed to ``.governance``. The
#     module survives as a shim for one release; the functions inside did not.
#  3. ``get_minio_credentials``, renamed to ``get_credentials``, whose result
#     also renamed ``access_key``/``secret_key`` to ``s3_access_key``/
#     ``s3_secret_key``.
#
# Prefer ``berdl_notebook_utils.get_s3_client()``, which builds the client and
# sidesteps all three.
DEAD_PATTERNS = {
    "settings attribute that no longer exists": re.compile(r"\.MINIO_[A-Z][A-Z0-9_]*\b"),
    # Import statements only. `scripts/ingest_lib.py` legitimately names the old
    # module as a string, because it stubs whatever `data_lakehouse_ingest`
    # imports and the shim is still there for one release.
    "module renamed to berdl_notebook_utils.governance": re.compile(
        r"^\s*(?:from\s+berdl_notebook_utils\.minio_governance\s+import"
        r"|import\s+berdl_notebook_utils\.minio_governance)\b"
    ),
    "function renamed to get_credentials": re.compile(r"\bget_minio_credentials\b"),
}

SKIP_DIRS = {".git", ".venv", ".venv-berdl", "node_modules", "__pycache__"}


def _python_files() -> list[Path]:
    out = []
    for path in REPO_ROOT.rglob("*.py"):
        if SKIP_DIRS & set(path.relative_to(REPO_ROOT).parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        out.append(path)
    return out


def test_no_python_file_uses_a_removed_berdl_api():
    """Nothing may use a BERDL name that a current pod no longer provides."""
    offenders = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            for why, pattern in DEAD_PATTERNS.items():
                if pattern.search(line):
                    rel = path.relative_to(REPO_ROOT)
                    offenders.append(f"{rel}:{lineno}: {why}\n      {line.strip()}")

    assert not offenders, (
        "These use a BERDL name that no longer exists, so they fail on a current "
        "pod. berdl_notebook_utils.get_s3_client() replaces all of them:\n  "
        + "\n  ".join(offenders)
    )


def test_the_guard_can_actually_fail():
    """A test that never fails guards nothing, so prove each pattern matches."""
    attr = DEAD_PATTERNS["settings attribute that no longer exists"]
    module = DEAD_PATTERNS["module renamed to berdl_notebook_utils.governance"]
    func = DEAD_PATTERNS["function renamed to get_credentials"]

    assert attr.search("endpoint = settings.MINIO_ENDPOINT_URL.replace(")
    assert attr.search("x = cfg.MINIO_SECRET_KEY")
    assert module.search(
        "from berdl_notebook_utils.minio_governance import get_credentials"
    )
    # a stub-list entry names the module as data, not as an import
    assert not module.search('    "berdl_notebook_utils.minio_governance",')
    assert func.search("creds = get_minio_credentials()")

    # and none of them fire on what they should leave alone
    assert not attr.search('os.environ["MINIO_ENDPOINT_URL"]')
    assert not attr.search("settings.S3_ENDPOINT_URL")
    assert not attr.search("# historically this was MINIO_ENDPOINT_URL")
    assert not module.search("from berdl_notebook_utils.governance import get_credentials")
    assert not func.search("creds = get_credentials()")
