"""Unit tests for the ingest gate's pieces (the route is tested in
test_routes_context.py's ``gated`` tests)."""

from __future__ import annotations

import ast
import io
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.routes.ingest_gate import (
    ALLOWED_FILES,
    archive_entry_count,
    disallowed,
    extract_members,
)

_REPO = Path(__file__).resolve().parents[2]


def _staged_names() -> set[str]:
    """``PROJECT_CURATED_NAMES`` from the mirror's own selection module.

    Read from source, not imported: the webapp does not depend on the
    ``observatory_context`` package.
    """
    source = (_REPO / "observatory_context" / "selection.py").read_text()
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "PROJECT_CURATED_NAMES" for t in node.targets
        ):
            return set(ast.literal_eval(node.value))
    raise AssertionError("PROJECT_CURATED_NAMES not found in selection.py")


def test_allowlist_matches_what_the_mirror_stages():
    """The allowlist is the mirror's curated files plus the two it generates.
    If the mirror starts staging a new file, the gate must learn it too — or
    every /submit of a project carrying that file is refused."""
    assert ALLOWED_FILES == _staged_names() | {"PROJECT_METADATA.md", "CLAIMS_CONTEXT.md"}


@pytest.mark.parametrize(
    "path, allowed",
    [
        ("REPORT.md", True),
        ("memories/discoveries.md", True),
        ("memories/anything-at-all.md", True),
        ("REFUTATION_1.md", True),
        ("REFUTATION_12.md", True),
        ("REFUTATION_0.md", False),
        ("memories/sub/x.md", False),
        ("memories/x.txt", False),
        ("report.md", False),
        ("notes/REPORT.md", False),
        ("figures/plot.png", False),
    ],
)
def test_disallowed(path, allowed):
    assert (disallowed([path]) == []) is allowed


def _zip(members: dict[str, bytes], *, symlink: str | None = None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
        if symlink:
            info = zipfile.ZipInfo(symlink)
            info.external_attr = 0o120777 << 16
            zf.writestr(info, "/etc/passwd")
    return buf.getvalue()


def _extract(tmp_path, archive, members, **limits):
    limits = {"max_file_bytes": 1_000, "max_total_bytes": 10_000, "max_entries": 100, **limits}
    extract_members(archive, tmp_path.resolve(), members, **limits)


def test_extracts_only_the_named_members(tmp_path):
    _extract(tmp_path, _zip({"REPORT.md": b"r", "other.bin": b"x"}), ["REPORT.md"])

    assert (tmp_path / "REPORT.md").read_bytes() == b"r"
    assert not (tmp_path / "other.bin").exists()


def test_refuses_a_member_over_the_per_file_limit_without_writing(tmp_path):
    with pytest.raises(HTTPException) as raised:
        _extract(tmp_path, _zip({"a.md": b"x" * 2_000}), ["a.md"])

    assert raised.value.status_code == 413
    assert not any(tmp_path.iterdir())


def test_refuses_an_expanded_total_over_the_limit_without_writing(tmp_path):
    members = {f"m{i}.md": b"x" * 900 for i in range(5)}
    with pytest.raises(HTTPException) as raised:
        _extract(tmp_path, _zip(members), list(members), max_total_bytes=4_000)

    assert raised.value.status_code == 413
    assert "expands to" in raised.value.detail
    assert not any(tmp_path.iterdir())


def test_refuses_a_symlink_member(tmp_path):
    with pytest.raises(HTTPException) as raised:
        _extract(tmp_path, _zip({}, symlink="link.md"), ["link.md"])

    assert raised.value.status_code == 400


def test_reports_members_missing_from_the_archive(tmp_path):
    with pytest.raises(HTTPException) as raised:
        _extract(tmp_path, _zip({"a.md": b"a"}), ["a.md", "gone.md"])

    assert raised.value.status_code == 422
    assert "gone.md" in raised.value.detail


def test_refuses_a_file_that_is_not_a_zip(tmp_path):
    with pytest.raises(HTTPException) as raised:
        _extract(tmp_path, b"not a zip", ["a.md"])

    assert raised.value.status_code == 400



def _flood(n: int, *, listed: dict[str, bytes] | None = None) -> bytes:
    """A small archive padded with ``n`` empty unlisted entries."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in (listed or {}).items():
            zf.writestr(name, data)
        for i in range(n):
            zf.writestr(f"pad/{i}", b"")
    return buf.getvalue()


def test_entry_count_is_read_without_parsing_the_directory():
    assert archive_entry_count(_flood(250)) == 250
    assert archive_entry_count(b"not a zip") is None


def test_entry_count_reads_the_zip64_end_record():
    """Past 65,535 entries the count lives only in the zip64 end record."""
    assert archive_entry_count(_flood(70_000)) == 70_000


def test_refuses_an_entry_flood_without_opening_the_archive(tmp_path, monkeypatch):
    """Regression (Codex adversarial review): the manifest selects a few
    members, but opening the archive materializes every entry — tens of
    thousands of empty ones fit well under the upload cap. The count is
    refused from the end record, so the directory is never parsed."""
    archive = _flood(5_000, listed={"REPORT.md": b"r"})

    def never(*args, **kwargs):
        raise AssertionError("the archive must not be opened")

    monkeypatch.setattr(zipfile, "ZipFile", never)
    with pytest.raises(HTTPException) as raised:
        _extract(tmp_path, archive, ["REPORT.md"], max_entries=1_000)

    assert raised.value.status_code == 413
    assert "5001 entries" in raised.value.detail
    assert not any(tmp_path.iterdir())


def test_admits_an_archive_at_the_entry_limit(tmp_path):
    archive = _flood(9, listed={"REPORT.md": b"r"})

    _extract(tmp_path, archive, ["REPORT.md"], max_entries=10)

    assert (tmp_path / "REPORT.md").read_bytes() == b"r"
