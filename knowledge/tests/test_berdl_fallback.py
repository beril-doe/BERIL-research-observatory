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


class _FakePaginator:
    def __init__(self, objects: dict[str, str]) -> None:
        self.objects = objects

    def paginate(self, *, Bucket: str, Prefix: str):
        contents = [
            {"Key": key} for key in self.objects if key.startswith(Prefix)
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


# --- credential / availability gating -------------------------------------


def test_no_credentials_makes_client_unavailable(monkeypatch):
    monkeypatch.setattr(bf, "_resolve_credentials", lambda: None)
    with pytest.raises(bf.BerdlUnavailable, match="credentials"):
        bf._s3_client()


def test_berdl_available_false_when_no_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(bf, "_resolve_credentials", lambda: None)
    assert bf.berdl_available(_config(tmp_path)) is False
