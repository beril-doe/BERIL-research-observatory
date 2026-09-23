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

import ast
import re
import warnings
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
    "function renamed to get_credentials": re.compile(r"\bget_minio_credentials\b"),
}

# The module rename is checked on parsed import statements, not on lines, so every
# layout counts: parenthesised multi-line imports, aliases, and the package-level
# ``from berdl_notebook_utils import minio_governance``. `scripts/ingest_lib.py`
# names the old module as a string, because it stubs whatever
# `data_lakehouse_ingest` imports while the shim lasts, and a string is not an import.
REMOVED_MODULE = "berdl_notebook_utils.minio_governance"
MODULE_WHY = "module renamed to berdl_notebook_utils.governance"


def removed_module_imports(source: str) -> list[int]:
    """Line numbers of every import of REMOVED_MODULE in ``source``."""
    with warnings.catch_warnings():
        # Old scripts carry invalid escape sequences; that is not this guard's concern.
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(source)
    package, _, leaf = REMOVED_MODULE.rpartition(".")
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name == REMOVED_MODULE or a.name.startswith(REMOVED_MODULE + ".")
                   for a in node.names):
                hits.append(node.lineno)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if node.module == REMOVED_MODULE or node.module.startswith(REMOVED_MODULE + "."):
                hits.append(node.lineno)
            elif node.module == package and any(a.name == leaf for a in node.names):
                hits.append(node.lineno)
    return hits


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
        rel = path.relative_to(REPO_ROOT)
        lines = text.splitlines()
        try:
            module_hits = removed_module_imports(text)
        except SyntaxError as exc:
            # Fail rather than skip: a file this cannot read is a file it cannot vouch for.
            offenders.append(f"{rel}:{exc.lineno}: cannot be parsed, so imports were not checked")
            module_hits = []
        for lineno in module_hits:
            offenders.append(f"{rel}:{lineno}: {MODULE_WHY}\n      {lines[lineno - 1].strip()}")
        for lineno, line in enumerate(lines, 1):
            for why, pattern in DEAD_PATTERNS.items():
                if pattern.search(line):
                    offenders.append(f"{rel}:{lineno}: {why}\n      {line.strip()}")

    assert not offenders, (
        "These use a BERDL name that no longer exists, so they fail on a current "
        "pod. berdl_notebook_utils.get_s3_client() replaces all of them:\n  "
        + "\n  ".join(offenders)
    )


def test_the_guard_can_actually_fail():
    """A test that never fails guards nothing, so prove each pattern matches."""
    attr = DEAD_PATTERNS["settings attribute that no longer exists"]
    module = removed_module_imports
    func = DEAD_PATTERNS["function renamed to get_credentials"]

    assert attr.search("endpoint = settings.MINIO_ENDPOINT_URL.replace(")
    assert attr.search("x = cfg.MINIO_SECRET_KEY")
    assert module(
        "from berdl_notebook_utils.minio_governance import get_credentials"
    )
    assert module("from berdl_notebook_utils import minio_governance")
    assert module("from berdl_notebook_utils import get_s3_client, minio_governance")
    assert module("from berdl_notebook_utils import (\n    get_s3_client,\n    minio_governance,\n)\n")
    assert module("import berdl_notebook_utils.minio_governance as mg")
    assert module("def f():\n    from berdl_notebook_utils.minio_governance import x\n") == [2]
    # a stub-list entry names the module as data, not as an import
    assert not module('STUBS = [\n    "berdl_notebook_utils.minio_governance",\n]\n')
    assert func.search("creds = get_minio_credentials()")

    # and none of them fire on what they should leave alone
    assert not attr.search('os.environ["MINIO_ENDPOINT_URL"]')
    assert not attr.search("settings.S3_ENDPOINT_URL")
    assert not attr.search("# historically this was MINIO_ENDPOINT_URL")
    assert not module("from berdl_notebook_utils.governance import get_credentials")
    assert not module("from berdl_notebook_utils import governance")
    assert not func.search("creds = get_credentials()")
