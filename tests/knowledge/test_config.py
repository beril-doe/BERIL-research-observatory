"""Tests for ContextConfig.from_env credential resolution.

The environment only: these tools reach the store directly, which is an
admin's job, so they never borrow a credential from a user's `beril login`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from beril_cli import auth_store
from observatory_context.config import (
    DEFAULT_OPENVIKING_URL,
    DEFAULT_S3_ENDPOINT_URL,
    DOCS_TARGET_URI,
    HOUSE_ACCOUNT_ID,
    PROJECTS_TARGET_URI,
    ContextConfig,
    s3_settings,
)


@pytest.fixture(autouse=True)
def clear_ov_env(monkeypatch):
    """Start each test from a known state — no OV env vars set."""
    monkeypatch.delenv("OPENVIKING_URL", raising=False)
    monkeypatch.delenv("OPENVIKING_API_KEY", raising=False)


@pytest.fixture
def clear_s3_env(monkeypatch):
    """Drop every S3/MinIO env var so each test defines its own state."""
    for name in (
        "S3_ENDPOINT_URL",
        "MINIO_ENDPOINT_URL",
        "S3_ACCESS_KEY",
        "MINIO_ACCESS_KEY",
        "S3_SECRET_KEY",
        "MINIO_SECRET_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


class TestFromEnv:
    def test_env_vars_are_used(self, monkeypatch):
        monkeypatch.setenv("OPENVIKING_URL", "https://env/ov")
        monkeypatch.setenv("OPENVIKING_API_KEY", "env_key")

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://env/ov"
        assert cfg.openviking_api_key == "env_key"

    def test_default_url_and_no_key_when_unset(self):
        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == DEFAULT_OPENVIKING_URL
        assert cfg.openviking_api_key is None

    def test_env_url_alone_is_kept(self, monkeypatch):
        # An unauthenticated local/dev store needs no key.
        monkeypatch.setenv("OPENVIKING_URL", "https://dev/ov")

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://dev/ov"
        assert cfg.openviking_api_key is None

    def test_a_store_key_left_by_an_older_login_is_never_used(self, tmp_path, monkeypatch):
        """`beril login` used to cache a per-user store key, and this fell back
        to it. Users no longer hold one; a key still sitting in an old
        auth.json must not be picked up."""
        auth = tmp_path / "auth.json"
        auth.write_text(
            '{"token": "t", "base_url": "https://srv", "orcid_id": "0",'
            ' "ov_url": "https://srv/ov", "ov_user_key": "legacy_ovk"}'
        )
        monkeypatch.setattr(auth_store, "AUTH_PATH", auth)

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == DEFAULT_OPENVIKING_URL
        assert cfg.openviking_api_key is None


class TestS3Settings:
    """`S3_*` env vars take precedence over legacy `MINIO_*`, symmetrically for
    endpoint and both keys. This is what makes the Ceph cutover an env change
    rather than a code edit — regression on any leg would silently break that."""

    def test_defaults_when_no_env(self, clear_s3_env):
        result = s3_settings()
        assert result == {
            "endpoint_url": DEFAULT_S3_ENDPOINT_URL,
            "access_key": None,
            "secret_key": None,
        }

    def test_minio_legacy_env_still_works(self, clear_s3_env, monkeypatch):
        monkeypatch.setenv("MINIO_ENDPOINT_URL", "https://minio.example/")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "minio-ak")
        monkeypatch.setenv("MINIO_SECRET_KEY", "minio-sk")

        result = s3_settings()
        assert result == {
            "endpoint_url": "https://minio.example/",
            "access_key": "minio-ak",
            "secret_key": "minio-sk",
        }

    def test_s3_env_wins_over_minio(self, clear_s3_env, monkeypatch):
        monkeypatch.setenv("S3_ENDPOINT_URL", "https://ceph.example/")
        monkeypatch.setenv("MINIO_ENDPOINT_URL", "https://minio.example/")
        monkeypatch.setenv("S3_ACCESS_KEY", "s3-ak")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "minio-ak")
        monkeypatch.setenv("S3_SECRET_KEY", "s3-sk")
        monkeypatch.setenv("MINIO_SECRET_KEY", "minio-sk")

        result = s3_settings()
        assert result == {
            "endpoint_url": "https://ceph.example/",
            "access_key": "s3-ak",
            "secret_key": "s3-sk",
        }

    def test_mixed_precedence_per_field(self, clear_s3_env, monkeypatch):
        # Each of endpoint/access/secret independently prefers S3_ over MINIO_,
        # so a partial rollout (S3_ACCESS_KEY set but not yet S3_SECRET_KEY)
        # still resolves cleanly instead of silently going all-legacy.
        monkeypatch.setenv("S3_ACCESS_KEY", "s3-ak")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "minio-ak")
        monkeypatch.setenv("MINIO_SECRET_KEY", "minio-sk")
        monkeypatch.setenv("MINIO_ENDPOINT_URL", "https://minio.example/")

        result = s3_settings()
        assert result == {
            "endpoint_url": "https://minio.example/",
            "access_key": "s3-ak",
            "secret_key": "minio-sk",
        }


def test_central_docs_live_under_the_house_account():
    """Pinned literally, not derived.

    BERIL's read routes address everything as ``resources/users/<owner>/…``, so
    the ownerless central docs sit under a reserved owner instead of needing a
    special case in every read path. A test that derived this value from the
    constant would not notice the root moving.
    """
    assert DOCS_TARGET_URI == "viking://resources/users/beril/docs/"


def test_house_account_matches_the_webapps_reserved_name():
    """The two definitions must agree.

    ``observatory_context`` cannot import the webapp (it must work without it
    on the path), so the name is duplicated. If they drift, the webapp reserves
    one name while ingest writes to another — and a real user could claim the
    namespace ingest is using.
    """
    ui_openviking = (
        Path(__file__).resolve().parents[2]
        / "ui" / "app" / "context_manager" / "openviking.py"
    )
    source = ui_openviking.read_text(encoding="utf-8")
    assert f'HOUSE_ACCOUNT_ID = "{HOUSE_ACCOUNT_ID}"' in source


def test_docs_and_projects_roots_stay_disjoint():
    """Prefix filters in ``ingest`` assume no target matches both."""
    assert not DOCS_TARGET_URI.startswith(PROJECTS_TARGET_URI)
    assert not PROJECTS_TARGET_URI.startswith(DOCS_TARGET_URI)
