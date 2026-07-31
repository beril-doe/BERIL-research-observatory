"""Tests for the BERDL lakehouse fallback tier.

Fully isolated: the boto3 client is stubbed via ``_s3_client`` and credential
resolution is stubbed via ``_resolve_credentials`` — no test touches the real
network, real MinIO/Ceph, real env credentials, or ``berdl-remote``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from observatory_context import berdl_fallback as bf
from observatory_context.config import ContextConfig, LAKEHOUSE_BUCKET


def _config(tmp_path: Path) -> ContextConfig:
    return ContextConfig(repo_root=tmp_path)


class _FakeBody:
    def __init__(self, text: str) -> None:
        self._data = text.encode("utf-8")

    def read(self) -> bytes:
        return self._data


_FIXED_MODTIME = "2026-07-24T16:53:46Z"


class _FakePaginator:
    def __init__(self, objects: dict[str, str]) -> None:
        self.objects = objects

    def paginate(self, *, Bucket: str, Prefix: str):
        contents = [
            {
                "Key": key,
                "Size": len(body.encode("utf-8")),
                "LastModified": _FIXED_MODTIME,
            }
            for key, body in self.objects.items()
            if key.startswith(Prefix)
        ]
        yield {"Contents": contents}


class _FakeS3:
    """Minimal stand-in for a boto3 S3 client backed by an in-memory store."""

    def __init__(self, objects: dict[str, str]) -> None:
        self.objects = objects  # key -> body text

    def get_object(self, *, Bucket: str, Key: str):
        if Key not in self.objects:
            raise ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": "missing"}}, "GetObject"
            )
        return {"Body": _FakeBody(self.objects[Key])}

    def head_object(self, *, Bucket: str, Key: str):
        if Key not in self.objects:
            raise ClientError(
                {"Error": {"Code": "404", "Message": "missing"}}, "HeadObject"
            )
        return {
            "ContentLength": len(self.objects[Key].encode("utf-8")),
            "LastModified": _FIXED_MODTIME,
        }

    def get_paginator(self, name: str):
        return _FakePaginator(self.objects)


def _patch_client(monkeypatch, client) -> None:
    monkeypatch.setattr(bf, "_s3_client", lambda: client)


# --- URI mapping ----------------------------------------------------------


def test_uri_to_bucket_key_maps_project_files():
    bucket, key = bf.uri_to_bucket_key("viking://resources/projects/alpha/README.md")
    assert bucket == LAKEHOUSE_BUCKET
    assert key.endswith("/projects/alpha/README.md")

    _, nested = bf.uri_to_bucket_key(
        "viking://resources/projects/alpha/memories/pitfalls.md"
    )
    assert nested.endswith("/projects/alpha/memories/pitfalls.md")


def test_uri_to_bucket_key_rejects_non_project_uris():
    # Docs and other resources are not archived in the lakehouse.
    with pytest.raises(bf.BerdlUnavailable):
        bf.uri_to_bucket_key("viking://resources/docs/pitfalls/pitfalls.md")
    with pytest.raises(bf.BerdlUnavailable):
        bf.uri_to_bucket_key("viking://resources/projects/")


# --- read -----------------------------------------------------------------


def test_berdl_read_returns_archived_content(tmp_path, monkeypatch):
    key = "tenant-general-warehouse/microbialdiscoveryforge/projects/alpha/README.md"
    _patch_client(monkeypatch, _FakeS3({key: "# Alpha\nArchived copy.\n"}))

    out = bf.berdl_read(_config(tmp_path), "viking://resources/projects/alpha/README.md")
    assert "Archived copy." in out


def test_berdl_read_missing_object_is_unavailable(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3({}))  # empty store -> NoSuchKey
    with pytest.raises(bf.BerdlUnavailable):
        bf.berdl_read(_config(tmp_path), "viking://resources/projects/alpha/README.md")


def test_berdl_read_access_denied_is_unavailable(tmp_path, monkeypatch):
    class _Denied:
        def get_object(self, **_):
            raise ClientError(
                {"Error": {"Code": "AccessDenied", "Message": "nope"}}, "GetObject"
            )

    _patch_client(monkeypatch, _Denied())
    with pytest.raises(bf.BerdlUnavailable, match="AccessDenied"):
        bf.berdl_read(_config(tmp_path), "viking://resources/projects/alpha/README.md")


def test_berdl_read_endpoint_unreachable_is_unavailable(tmp_path, monkeypatch):
    class _Unreachable:
        def get_object(self, **_):
            raise EndpointConnectionError(endpoint_url="https://minio.example")

    _patch_client(monkeypatch, _Unreachable())
    with pytest.raises(bf.BerdlUnavailable, match="unreachable"):
        bf.berdl_read(_config(tmp_path), "viking://resources/projects/alpha/README.md")


# --- overview -------------------------------------------------------------


def test_berdl_overview_directory_reads_readme(tmp_path, monkeypatch):
    key = "tenant-general-warehouse/microbialdiscoveryforge/projects/alpha/README.md"
    body = "line1\nline2\n" + "\n".join(f"extra{i}" for i in range(60))
    _patch_client(monkeypatch, _FakeS3({key: body}))

    out = bf.berdl_overview(_config(tmp_path), "viking://resources/projects/alpha/")
    assert out.splitlines()[0] == "line1"
    # Overview is capped at the first 40 lines.
    assert len(out.splitlines()) <= 40


def test_berdl_overview_file_returns_file(tmp_path, monkeypatch):
    key = "tenant-general-warehouse/microbialdiscoveryforge/projects/alpha/REPORT.md"
    _patch_client(monkeypatch, _FakeS3({key: "# Report\nbody\n"}))

    out = bf.berdl_overview(
        _config(tmp_path), "viking://resources/projects/alpha/REPORT.md"
    )
    assert "# Report" in out


# --- find (keyword search over the archived corpus) -----------------------

_TENANT = "tenant-general-warehouse/microbialdiscoveryforge/projects"


def test_berdl_find_scores_curated_files_and_skips_non_corpus(tmp_path, monkeypatch):
    store = {
        f"{_TENANT}/alpha/README.md": "# Alpha\nStudies phage timing in soil.\n",
        f"{_TENANT}/alpha/memories/pitfalls.md": "Spark OOM on the big table.\n",
        # non-corpus content must never be fetched or scored
        f"{_TENANT}/alpha/data/notes.md": "phage phage phage timing\n",
        f"{_TENANT}/alpha/notebooks/nb.ipynb": "phage timing\n",
    }
    _patch_client(monkeypatch, _FakeS3(store))

    result = bf.berdl_find(
        _config(tmp_path), "phage timing", "viking://resources/projects/", 10
    )

    assert result["source"] == "berdl"
    assert result["degraded"] is True
    uris = [r["uri"] for r in result["resources"]]
    assert "viking://resources/projects/alpha/README.md" in uris
    # data/ and notebooks/ are outside the curated corpus -> never returned.
    assert all("/data/" not in u and "/notebooks/" not in u for u in uris)


def test_berdl_find_single_project_scope(tmp_path, monkeypatch):
    store = {
        f"{_TENANT}/alpha/README.md": "alpha readme mentions spark\n",
        f"{_TENANT}/beta/README.md": "beta readme mentions spark\n",
    }
    _patch_client(monkeypatch, _FakeS3(store))

    result = bf.berdl_find(
        _config(tmp_path), "spark", "viking://resources/projects/alpha/", 10
    )
    uris = [r["uri"] for r in result["resources"]]
    assert uris == ["viking://resources/projects/alpha/README.md"]


def test_berdl_find_docs_scope_is_unavailable(tmp_path, monkeypatch):
    # Docs aren't archived in the lakehouse -> caller falls back to local.
    _patch_client(monkeypatch, _FakeS3({}))
    with pytest.raises(bf.BerdlUnavailable):
        bf.berdl_find(_config(tmp_path), "spark", "viking://resources/docs/", 10)


# --- grep (exact line-match over the archived corpus) ---------------------


def test_berdl_grep_matches_curated_and_reports_lines(tmp_path, monkeypatch):
    store = {
        f"{_TENANT}/alpha/README.md": "line one\nSpark timeout here\nline three\n",
        f"{_TENANT}/alpha/memories/pitfalls.md": "Spark OOM on the big table\n",
        # non-corpus: must never be searched even though it matches
        f"{_TENANT}/alpha/data/log.md": "Spark Spark Spark\n",
    }
    _patch_client(monkeypatch, _FakeS3(store))

    result = bf.berdl_grep(_config(tmp_path), "Spark", "viking://resources/")

    assert result["source"] == "berdl"
    hit_uris = {m["uri"] for m in result["matches"]}
    assert "viking://resources/projects/alpha/README.md" in hit_uris
    assert "viking://resources/projects/alpha/memories/pitfalls.md" in hit_uris
    assert all("/data/" not in m["uri"] for m in result["matches"])
    # line numbers are 1-based within the file
    readme_hit = next(m for m in result["matches"] if m["uri"].endswith("README.md"))
    assert readme_hit["line"] == 2


def test_berdl_grep_respects_exclude_and_node_limit(tmp_path, monkeypatch):
    store = {
        f"{_TENANT}/alpha/README.md": "spark\nspark\nspark\n",
        f"{_TENANT}/beta/README.md": "spark\n",
    }
    _patch_client(monkeypatch, _FakeS3(store))

    limited = bf.berdl_grep(_config(tmp_path), "spark", "viking://resources/", node_limit=2)
    assert len(limited["matches"]) == 2

    excluded = bf.berdl_grep(
        _config(tmp_path),
        "spark",
        "viking://resources/",
        exclude_uri="viking://resources/projects/beta/",
    )
    assert all("/projects/beta/" not in m["uri"] for m in excluded["matches"])


def test_berdl_grep_docs_scope_is_unavailable(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3({}))
    with pytest.raises(bf.BerdlUnavailable):
        bf.berdl_grep(_config(tmp_path), "spark", "viking://resources/docs/")


# --- structural navigation (ls / glob / tree / stat) ----------------------

# Shape parity: field sets asserted below mirror the live OpenViking output
# (ls/tree entries: name/size/mode/modTime/isDir/uri; stat adds count for dirs;
# glob: {matches, count}).
_LS_FIELDS = {"name", "size", "mode", "modTime", "isDir", "uri"}


def _tree_store() -> dict[str, str]:
    return {
        f"{_TENANT}/alpha/README.md": "readme\n",
        f"{_TENANT}/alpha/beril.yaml": "y\n",
        f"{_TENANT}/alpha/data/results.tsv": "a\tb\n",
        f"{_TENANT}/alpha/memories/pitfalls.md": "p\n",
    }


def test_berdl_ls_non_recursive_lists_files_and_synthesized_dirs(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))

    entries = bf.berdl_ls(_config(tmp_path), "viking://resources/projects/alpha/")

    assert isinstance(entries, list)
    for e in entries:
        assert _LS_FIELDS <= set(e)  # shape parity with OpenViking ls
    by_uri = {e["uri"]: e for e in entries}
    # direct files present as non-dir entries
    assert by_uri["viking://resources/projects/alpha/README.md"]["isDir"] is False
    # data/ and memories/ collapse to synthesized directory entries (dir URIs
    # carry no trailing slash, matching OpenViking's ls output)
    assert by_uri["viking://resources/projects/alpha/data"]["isDir"] is True
    assert by_uri["viking://resources/projects/alpha/memories"]["isDir"] is True
    # non-recursive: results.tsv itself is NOT a top-level entry
    assert "viking://resources/projects/alpha/data/results.tsv" not in by_uri


def test_berdl_ls_simple_returns_uri_strings(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    out = bf.berdl_ls(_config(tmp_path), "viking://resources/projects/alpha/", simple=True)
    assert all(isinstance(u, str) and u.startswith("viking://") for u in out)


def test_berdl_ls_recursive_includes_nested(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    entries = bf.berdl_ls(
        _config(tmp_path), "viking://resources/projects/alpha/", recursive=True
    )
    uris = {e["uri"] for e in entries}
    assert "viking://resources/projects/alpha/data/results.tsv" in uris
    assert "viking://resources/projects/alpha/memories/pitfalls.md" in uris


def test_berdl_glob_matches_relative_pattern(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    result = bf.berdl_glob(
        _config(tmp_path), "**/*.md", "viking://resources/projects/alpha/"
    )
    assert set(result) == {"matches", "count"}  # shape parity with OpenViking glob
    assert result["count"] == len(result["matches"])
    assert "viking://resources/projects/alpha/README.md" in result["matches"]
    assert "viking://resources/projects/alpha/memories/pitfalls.md" in result["matches"]
    # beril.yaml is not a .md file
    assert all(m.endswith(".md") for m in result["matches"])


def test_berdl_glob_single_star_stays_within_segment(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    result = bf.berdl_glob(_config(tmp_path), "*", "viking://resources/projects/alpha/")
    # '*' matches only direct children, not nested paths
    assert "viking://resources/projects/alpha/README.md" in result["matches"]
    assert "viking://resources/projects/alpha/data/results.tsv" not in result["matches"]


def test_berdl_tree_is_flat_preorder_with_rel_path(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    entries = bf.berdl_tree(_config(tmp_path), "viking://resources/projects/alpha/")

    assert isinstance(entries, list)
    for e in entries:
        assert _LS_FIELDS <= set(e)
        assert "rel_path" in e  # tree adds rel_path
    rel_paths = [e["rel_path"] for e in entries]
    # a directory entry precedes the file inside it (pre-order)
    assert rel_paths.index("data") < rel_paths.index("data/results.tsv")


def test_berdl_tree_respects_node_limit(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    entries = bf.berdl_tree(
        _config(tmp_path), "viking://resources/projects/alpha/", node_limit=2
    )
    assert len(entries) == 2


def test_berdl_stat_file_uses_head_object(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    result = bf.berdl_stat(
        _config(tmp_path), "viking://resources/projects/alpha/README.md"
    )
    assert result["isDir"] is False
    assert result["name"] == "README.md"
    assert result["size"] == len("readme\n".encode("utf-8"))


def test_berdl_stat_directory_aggregates_count(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3(_tree_store()))
    result = bf.berdl_stat(_config(tmp_path), "viking://resources/projects/alpha/")
    assert result["isDir"] is True
    assert result["count"] == len(_tree_store())
    assert result["name"] == "alpha"


def test_berdl_stat_missing_is_unavailable(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3({}))
    with pytest.raises(bf.BerdlUnavailable):
        bf.berdl_stat(_config(tmp_path), "viking://resources/projects/ghost/")


def test_structural_docs_scope_is_unavailable(tmp_path, monkeypatch):
    _patch_client(monkeypatch, _FakeS3({}))
    for call in (
        lambda: bf.berdl_ls(_config(tmp_path), "viking://resources/docs/"),
        lambda: bf.berdl_glob(_config(tmp_path), "*", "viking://resources/docs/"),
        lambda: bf.berdl_tree(_config(tmp_path), "viking://resources/docs/"),
    ):
        with pytest.raises(bf.BerdlUnavailable):
            call()


# --- credential / availability gating -------------------------------------


def test_no_credentials_makes_client_unavailable(monkeypatch):
    monkeypatch.setattr(bf, "_resolve_credentials", lambda: None)
    with pytest.raises(bf.BerdlUnavailable, match="credentials"):
        bf._s3_client()


def test_berdl_available_false_when_no_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(bf, "_resolve_credentials", lambda: None)
    assert bf.berdl_available(_config(tmp_path)) is False
