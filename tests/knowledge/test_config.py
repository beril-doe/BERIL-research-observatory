"""Tests for ContextConfig.from_env credential resolution.

Precedence: explicit env vars win, then the credential cached by
`beril login` / `beril ov setup` in ~/.beril, then the local default URL.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from observatory_context import config as ovcfg
from observatory_context.config import (
    DEFAULT_OPENVIKING_URL,
    DEFAULT_S3_ENDPOINT_URL,
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


def _patch_cache(monkeypatch, value):
    """Stub the ~/.beril cached-credential lookup."""
    monkeypatch.setattr(ovcfg, "_cached_ov_credential", lambda: value)


class TestFromEnvPrecedence:
    def test_env_vars_win(self, monkeypatch):
        monkeypatch.setenv("OPENVIKING_URL", "https://env/ov")
        monkeypatch.setenv("OPENVIKING_API_KEY", "env_key")
        _patch_cache(monkeypatch, ("https://cached/ov", "cached_key"))

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://env/ov"
        assert cfg.openviking_api_key == "env_key"

    def test_falls_back_to_cached_credential(self, monkeypatch):
        _patch_cache(monkeypatch, ("https://cached/ov", "cached_key"))

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://cached/ov"
        assert cfg.openviking_api_key == "cached_key"

    def test_default_url_when_nothing_available(self, monkeypatch):
        _patch_cache(monkeypatch, (None, None))

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == DEFAULT_OPENVIKING_URL
        assert cfg.openviking_api_key is None

    def test_partial_env_url_does_not_splice_cached_key(self, monkeypatch):
        # A partial env override (URL only, no key) must NOT borrow the cached
        # key: that would point a real cached key (e.g. prod) at whatever URL
        # the env named (e.g. a local dev OV) — a mismatched pair. Instead the
        # whole cached pair is taken as a unit, because it's complete.
        monkeypatch.setenv("OPENVIKING_URL", "https://env/ov")
        _patch_cache(monkeypatch, ("https://cached/ov", "cached_key"))

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://cached/ov"
        assert cfg.openviking_api_key == "cached_key"

    def test_partial_env_url_kept_when_no_cached_pair(self, monkeypatch):
        # With only a URL in the env and nothing cached, keep the env URL and
        # leave the key None — valid for an unauthenticated local/dev OpenViking.
        # (Regression guard: the pair-resolution must not drop the env URL back
        # to the default just because the key is absent.)
        monkeypatch.setenv("OPENVIKING_URL", "https://dev/ov")
        _patch_cache(monkeypatch, (None, None))

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://dev/ov"
        assert cfg.openviking_api_key is None


class TestCachedCredentialImportGuard:
    def test_returns_none_pair_when_beril_cli_absent(self, monkeypatch):
        # Simulate an environment where beril_cli isn't importable.
        import builtins

        real_import = builtins.__import__

        def _fake_import(name, *args, **kwargs):
            if name.startswith("beril_cli"):
                raise ImportError("no beril_cli here")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fake_import)
        assert ovcfg._cached_ov_credential() == (None, None)

    def test_returns_none_pair_when_not_linked(self, monkeypatch):
        from beril_cli import auth_store

        monkeypatch.setattr(auth_store, "load_ov", lambda: None)
        assert ovcfg._cached_ov_credential() == (None, None)

    def test_returns_pair_from_auth_store(self, monkeypatch):
        from beril_cli import auth_store

        monkeypatch.setattr(
            auth_store, "load_ov", lambda: ("https://srv/ov", "k")
        )
        assert ovcfg._cached_ov_credential() == ("https://srv/ov", "k")


class TestS3Settings:
    """Only the `S3_*` env vars are read, for the endpoint and both keys.

    BERDL renamed these from `MINIO_*` to `S3_*` and sets only the new names on a
    pod (verified there 2026-08-14). Reading `MINIO_*` as well would let a stale
    value on a developer machine resolve instead of the real one, so the tests
    below assert those names are ignored rather than merely unused."""

    def test_defaults_when_no_env(self, clear_s3_env):
        result = s3_settings()
        assert result == {
            "endpoint_url": DEFAULT_S3_ENDPOINT_URL,
            "access_key": None,
            "secret_key": None,
        }

    def test_minio_names_are_ignored(self, clear_s3_env, monkeypatch):
        # A machine still carrying the old exports must resolve as unconfigured,
        # not as configured with stale values.
        monkeypatch.setenv("MINIO_ENDPOINT_URL", "https://minio.example/")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "minio-ak")
        monkeypatch.setenv("MINIO_SECRET_KEY", "minio-sk")

        result = s3_settings()
        assert result == {
            "endpoint_url": DEFAULT_S3_ENDPOINT_URL,
            "access_key": None,
            "secret_key": None,
        }

    def test_s3_names_win_when_both_are_set(self, clear_s3_env, monkeypatch):
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

    def test_partial_s3_config_does_not_fall_back(self, clear_s3_env, monkeypatch):
        # Endpoint and both keys resolve independently. With only S3_ACCESS_KEY
        # set, the other two stay unset rather than picking up a MINIO_ value.
        monkeypatch.setenv("S3_ACCESS_KEY", "s3-ak")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "minio-ak")
        monkeypatch.setenv("MINIO_SECRET_KEY", "minio-sk")
        monkeypatch.setenv("MINIO_ENDPOINT_URL", "https://minio.example/")

        result = s3_settings()
        assert result == {
            "endpoint_url": DEFAULT_S3_ENDPOINT_URL,
            "access_key": "s3-ak",
            "secret_key": None,
        }
