"""Tests for ContextConfig.from_env credential resolution.

Precedence: explicit env vars win, then the credential cached by
`beril login` / `beril ov setup` in ~/.beril, then the local default URL.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from observatory_context import config as ovcfg
from observatory_context.config import DEFAULT_OPENVIKING_URL, ContextConfig


@pytest.fixture(autouse=True)
def clear_ov_env(monkeypatch):
    """Start each test from a known state — no OV env vars set."""
    monkeypatch.delenv("OPENVIKING_URL", raising=False)
    monkeypatch.delenv("OPENVIKING_API_KEY", raising=False)


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

    def test_env_url_with_cached_key_do_not_mix_when_both_env_present(
        self, monkeypatch
    ):
        # If only the URL is set in the env, the key is drawn from the cache —
        # partial env config still gets completed from ~/.beril.
        monkeypatch.setenv("OPENVIKING_URL", "https://env/ov")
        _patch_cache(monkeypatch, ("https://cached/ov", "cached_key"))

        cfg = ContextConfig.from_env(repo_root=Path("."))
        assert cfg.openviking_url == "https://env/ov"
        assert cfg.openviking_api_key == "cached_key"


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
