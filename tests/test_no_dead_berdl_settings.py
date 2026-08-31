"""Guard against reading BERDL settings attributes that no longer exist.

BERDL renamed its object-store settings from ``MINIO_*`` to ``S3_*``. A current
pod's ``BERDLSettings`` has ``S3_ACCESS_KEY``, ``S3_SECRET_KEY``,
``S3_ENDPOINT_URL`` and ``S3_SECURE``, and no ``MINIO_*`` attribute at all, so
``settings.MINIO_ENDPOINT_URL`` raises ``AttributeError`` rather than returning a
stale value.

That failure only shows up when a script is actually run on a pod, which is why
it survived in eight `data/` scripts for months. This test is static: it needs no
pod, no credentials and no BERDL packages, so CI catches a reintroduction the
same day rather than the next time someone runs an ingest.

Fixed across three pull requests before this guard existed: 380 (the credential
resolver and skill docs), 401 (``observatory_context/config.py``) and 381 (the
eight `data/` ingest scripts).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Attribute access on a settings object, e.g. ``settings.MINIO_ENDPOINT_URL``.
# Deliberately not matching ``os.environ["MINIO_..."]`` or prose: an env var that
# is merely absent gives a clean fallback, while a missing attribute raises.
DEAD_ATTRIBUTE = re.compile(r"\.MINIO_[A-Z][A-Z0-9_]*\b")

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


def test_no_python_file_reads_a_minio_settings_attribute():
    """No file may read ``<settings>.MINIO_*``; BERDL no longer defines those."""
    offenders = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if DEAD_ATTRIBUTE.search(line):
                rel = path.relative_to(REPO_ROOT)
                offenders.append(f"{rel}:{lineno}: {line.strip()}")

    assert not offenders, (
        "These read a BERDL settings attribute that no longer exists and will "
        "raise AttributeError on a current pod. Use the S3_* name instead:\n  "
        + "\n  ".join(offenders)
    )


def test_the_guard_can_actually_fail():
    """A test that never fails guards nothing, so prove the pattern matches."""
    assert DEAD_ATTRIBUTE.search("endpoint = settings.MINIO_ENDPOINT_URL.replace(")
    assert DEAD_ATTRIBUTE.search("x = cfg.MINIO_SECRET_KEY")
    # and does not fire on the things it should leave alone
    assert not DEAD_ATTRIBUTE.search('os.environ["MINIO_ENDPOINT_URL"]')
    assert not DEAD_ATTRIBUTE.search("settings.S3_ENDPOINT_URL")
    assert not DEAD_ATTRIBUTE.search("# historically this was MINIO_ENDPOINT_URL")
