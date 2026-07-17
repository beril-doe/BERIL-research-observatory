"""Tests for `beril auth` subcommand and its supporting modules."""

from __future__ import annotations

import argparse
import io
import json
import os
import stat
import sys
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from beril_cli import auth_cmd, auth_store, config
from beril_cli.auth_cmd import run_auth


# ---------------------------------------------------------------------------
# Shared fixtures — redirect on-disk paths into tmp_path
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_auth(tmp_path, monkeypatch):
    """Redirect auth_store's on-disk location into tmp_path."""
    auth_dir = tmp_path / ".beril"
    auth_path = auth_dir / "auth.json"
    monkeypatch.setattr(auth_store, "AUTH_DIR", auth_dir)
    monkeypatch.setattr(auth_store, "AUTH_PATH", auth_path)
    return auth_path


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Redirect config's on-disk location into tmp_path."""
    cfg_dir = tmp_path / ".config" / "beril"
    cfg_dir.mkdir(parents=True)
    cfg_path = cfg_dir / "config.toml"
    monkeypatch.setattr(config, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(config, "CONFIG_PATH", cfg_path)
    # Also clear any base-url env var so tests start from a known baseline.
    monkeypatch.delenv("BERIL_BASE_URL", raising=False)
    return cfg_path


def _ns(**kwargs) -> argparse.Namespace:
    """Build a Namespace with the flags run_auth expects."""
    defaults = {"action": None, "token": None, "base_url": None, "json": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _mock_whoami_response(body: dict, status: int = 200):
    """Build a context-manager-shaped mock for urlopen returning the given body."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(body).encode()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# auth_store
# ---------------------------------------------------------------------------


class TestAuthStore:
    def test_load_returns_none_when_missing(self, tmp_auth):
        assert auth_store.load() is None

    def test_save_then_load_round_trip(self, tmp_auth):
        auth_store.save(
            token="beril_abc",
            base_url="https://example.test",
            orcid_id="0000-0001-2345-6789",
            display_name="Alice",
        )
        record = auth_store.load()
        assert record is not None
        assert record["token"] == "beril_abc"
        assert record["base_url"] == "https://example.test"
        assert record["orcid_id"] == "0000-0001-2345-6789"
        assert record["display_name"] == "Alice"

    def test_save_creates_parent_dir(self, tmp_auth):
        assert not tmp_auth.parent.exists()
        auth_store.save(
            token="t", base_url="u", orcid_id="0", display_name=None
        )
        assert tmp_auth.parent.is_dir()

    @pytest.mark.skipif(
        sys.platform == "win32", reason="POSIX file mode semantics"
    )
    def test_save_sets_mode_0600(self, tmp_auth):
        auth_store.save(token="t", base_url="u", orcid_id="0", display_name=None)
        mode = stat.S_IMODE(tmp_auth.stat().st_mode)
        assert mode == 0o600

    def test_save_overwrites_existing(self, tmp_auth):
        auth_store.save(token="t1", base_url="u", orcid_id="0", display_name=None)
        auth_store.save(token="t2", base_url="u", orcid_id="0", display_name=None)
        assert auth_store.load()["token"] == "t2"

    def test_load_returns_none_for_corrupt_json(self, tmp_auth):
        tmp_auth.parent.mkdir(parents=True)
        tmp_auth.write_text("{not json")
        assert auth_store.load() is None

    def test_load_returns_none_for_missing_required_field(self, tmp_auth):
        tmp_auth.parent.mkdir(parents=True)
        tmp_auth.write_text(json.dumps({"token": "t"}))  # no base_url, no orcid
        assert auth_store.load() is None

    def test_load_backfills_missing_display_name(self, tmp_auth):
        tmp_auth.parent.mkdir(parents=True)
        tmp_auth.write_text(
            json.dumps({"token": "t", "base_url": "u", "orcid_id": "0"})
        )
        record = auth_store.load()
        assert record is not None
        assert record["display_name"] is None

    def test_clear_is_idempotent_when_missing(self, tmp_auth):
        # Should not raise
        auth_store.clear()
        auth_store.clear()

    def test_clear_removes_existing_file(self, tmp_auth):
        auth_store.save(token="t", base_url="u", orcid_id="0", display_name=None)
        assert tmp_auth.exists()
        auth_store.clear()
        assert not tmp_auth.exists()


# ---------------------------------------------------------------------------
# config.get_base_url / set_base_url
# ---------------------------------------------------------------------------


class TestBaseUrlResolution:
    def test_default_when_nothing_set(self, tmp_config):
        assert config.get_base_url() == config.DEFAULT_BASE_URL

    def test_env_var_overrides_default(self, tmp_config, monkeypatch):
        monkeypatch.setenv("BERIL_BASE_URL", "https://env.example.test/")
        assert config.get_base_url() == "https://env.example.test"

    def test_config_file_overrides_default(self, tmp_config):
        config.save({"beril": {"base_url": "https://cfg.example.test"}})
        assert config.get_base_url() == "https://cfg.example.test"

    def test_env_var_beats_config_file(self, tmp_config, monkeypatch):
        config.save({"beril": {"base_url": "https://cfg.example.test"}})
        monkeypatch.setenv("BERIL_BASE_URL", "https://env.example.test")
        assert config.get_base_url() == "https://env.example.test"

    def test_trailing_slash_is_stripped(self, tmp_config):
        config.save({"beril": {"base_url": "https://cfg.example.test/"}})
        assert config.get_base_url() == "https://cfg.example.test"

    def test_set_base_url_persists(self, tmp_config):
        config.set_base_url("https://new.example.test/")
        # Reload from disk to prove persistence, not in-memory retention.
        reloaded = config.load()
        assert reloaded["beril"]["base_url"] == "https://new.example.test"

    def test_set_base_url_preserves_other_sections(self, tmp_config):
        config.save({"user": {"name": "Alice"}, "defaults": {"agent": "claude"}})
        config.set_base_url("https://new.example.test")
        reloaded = config.load()
        assert reloaded["user"]["name"] == "Alice"
        assert reloaded["defaults"]["agent"] == "claude"
        assert reloaded["beril"]["base_url"] == "https://new.example.test"


# ---------------------------------------------------------------------------
# run_auth login
# ---------------------------------------------------------------------------


class TestAuthLogin:
    def test_login_with_token_flag_saves_record(
        self, tmp_auth, tmp_config, capsys
    ):
        response = _mock_whoami_response(
            {"orcid_id": "0000-0001-2345-6789", "display_name": "Alice"}
        )
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=response
        ):
            rc = run_auth(
                _ns(
                    action="login",
                    token="beril_abc",
                    base_url="https://srv.example.test",
                )
            )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Alice" in out
        assert "0000-0001-2345-6789" in out

        record = auth_store.load()
        assert record is not None
        assert record["token"] == "beril_abc"
        assert record["base_url"] == "https://srv.example.test"
        assert record["orcid_id"] == "0000-0001-2345-6789"

    def test_login_persists_base_url_flag(self, tmp_auth, tmp_config):
        response = _mock_whoami_response(
            {"orcid_id": "0000-0001-2345-6789", "display_name": None}
        )
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=response
        ):
            run_auth(
                _ns(
                    action="login",
                    token="beril_abc",
                    base_url="https://srv.example.test/",
                )
            )
        # The base URL should now be persisted (trailing slash stripped).
        assert config.get_base_url() == "https://srv.example.test"

    def test_login_hits_correct_whoami_url_with_bearer_header(
        self, tmp_auth, tmp_config
    ):
        response = _mock_whoami_response(
            {"orcid_id": "0000-0001-2345-6789", "display_name": None}
        )
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=response
        ) as mock_urlopen:
            run_auth(
                _ns(
                    action="login",
                    token="beril_abc",
                    base_url="https://srv.example.test",
                )
            )
        req = mock_urlopen.call_args.args[0]
        assert req.full_url == "https://srv.example.test/api/user/whoami"
        assert req.headers["Authorization"] == "Bearer beril_abc"

    def test_login_401_prints_error_and_does_not_save(
        self, tmp_auth, tmp_config, capsys
    ):
        err = urllib.error.HTTPError(
            "url", 401, "Unauthorized", hdrs=None, fp=io.BytesIO(b"")
        )
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", side_effect=err
        ):
            rc = run_auth(
                _ns(
                    action="login",
                    token="bad",
                    base_url="https://srv.example.test",
                )
            )
        captured = capsys.readouterr()
        assert rc == 1
        assert "401" in captured.err or "rejected" in captured.err
        assert auth_store.load() is None

    def test_login_connection_error_reports_reason(
        self, tmp_auth, tmp_config, capsys
    ):
        err = urllib.error.URLError("connection refused")
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", side_effect=err
        ):
            rc = run_auth(
                _ns(
                    action="login",
                    token="beril_abc",
                    base_url="https://srv.example.test",
                )
            )
        captured = capsys.readouterr()
        assert rc == 1
        assert "connection refused" in captured.err
        assert auth_store.load() is None

    def test_login_bad_json_response_fails(self, tmp_auth, tmp_config, capsys):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=mock_resp
        ):
            rc = run_auth(
                _ns(
                    action="login",
                    token="beril_abc",
                    base_url="https://srv.example.test",
                )
            )
        captured = capsys.readouterr()
        assert rc == 1
        assert "invalid JSON" in captured.err
        assert auth_store.load() is None

    def test_login_missing_orcid_in_response_fails(
        self, tmp_auth, tmp_config, capsys
    ):
        response = _mock_whoami_response({"display_name": "Alice"})
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=response
        ):
            rc = run_auth(
                _ns(
                    action="login",
                    token="beril_abc",
                    base_url="https://srv.example.test",
                )
            )
        assert rc == 1
        assert auth_store.load() is None

    def test_login_prompts_for_token_when_not_given(
        self, tmp_auth, tmp_config, monkeypatch
    ):
        response = _mock_whoami_response(
            {"orcid_id": "0000-0001-2345-6789", "display_name": "Alice"}
        )
        monkeypatch.setattr(auth_cmd.getpass, "getpass", lambda _prompt: "beril_pasted")
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=response
        ):
            rc = run_auth(
                _ns(
                    action="login",
                    token=None,
                    base_url="https://srv.example.test",
                )
            )
        assert rc == 0
        assert auth_store.load()["token"] == "beril_pasted"

    def test_login_empty_paste_exits_1(self, tmp_auth, tmp_config, monkeypatch, capsys):
        monkeypatch.setattr(auth_cmd.getpass, "getpass", lambda _prompt: "")
        rc = run_auth(
            _ns(
                action="login",
                token=None,
                base_url="https://srv.example.test",
            )
        )
        assert rc == 1
        assert "No token provided" in capsys.readouterr().err
        assert auth_store.load() is None


# ---------------------------------------------------------------------------
# run_auth status
# ---------------------------------------------------------------------------


class TestAuthStatus:
    def test_not_logged_in_returns_1(self, tmp_auth, capsys):
        rc = run_auth(_ns(action="status"))
        assert rc == 1
        assert "Not logged in" in capsys.readouterr().out

    def test_logged_in_prints_identity(self, tmp_auth, capsys):
        auth_store.save(
            token="beril_abc",
            base_url="https://srv.example.test",
            orcid_id="0000-0001-2345-6789",
            display_name="Alice",
        )
        rc = run_auth(_ns(action="status"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Alice" in out
        assert "0000-0001-2345-6789" in out
        assert "https://srv.example.test" in out
        # Never print the raw token in human-facing status.
        assert "beril_abc" not in out

    def test_status_json_omits_token(self, tmp_auth, capsys):
        auth_store.save(
            token="beril_abc",
            base_url="https://srv.example.test",
            orcid_id="0000-0001-2345-6789",
            display_name="Alice",
        )
        rc = run_auth(_ns(action="status", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        payload = json.loads(out)
        assert "token" not in payload
        assert payload["orcid_id"] == "0000-0001-2345-6789"
        assert payload["display_name"] == "Alice"
        assert payload["base_url"] == "https://srv.example.test"
        assert payload["path"].endswith("auth.json")


# ---------------------------------------------------------------------------
# run_auth logout
# ---------------------------------------------------------------------------


class TestAuthLogout:
    def test_logout_when_logged_in_removes_file(self, tmp_auth, capsys):
        auth_store.save(
            token="t", base_url="u", orcid_id="0", display_name=None
        )
        rc = run_auth(_ns(action="logout"))
        assert rc == 0
        assert "Logged out" in capsys.readouterr().out
        assert auth_store.load() is None

    def test_logout_when_not_logged_in_is_noop(self, tmp_auth, capsys):
        rc = run_auth(_ns(action="logout"))
        assert rc == 0
        assert "nothing to do" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# CLI dispatch smoke test (goes through main())
# ---------------------------------------------------------------------------


class TestCliDispatch:
    def test_beril_auth_login_dispatches(self, tmp_auth, tmp_config):
        from beril_cli.cli import main

        response = _mock_whoami_response(
            {"orcid_id": "0000-0001-2345-6789", "display_name": "Alice"}
        )
        with patch(
            "beril_cli.auth_cmd.urllib.request.urlopen", return_value=response
        ):
            rc = main(
                [
                    "auth",
                    "login",
                    "--token",
                    "beril_abc",
                    "--base-url",
                    "https://srv.example.test",
                ]
            )
        assert rc == 0
        assert auth_store.load()["token"] == "beril_abc"

    def test_beril_auth_status_dispatches(self, tmp_auth, capsys):
        from beril_cli.cli import main

        rc = main(["auth", "status"])
        assert rc == 1
        assert "Not logged in" in capsys.readouterr().out

    def test_beril_auth_logout_dispatches(self, tmp_auth):
        from beril_cli.cli import main

        rc = main(["auth", "logout"])
        assert rc == 0
