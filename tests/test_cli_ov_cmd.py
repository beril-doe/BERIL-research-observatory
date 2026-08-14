"""Tests for `beril ov` (ov_cmd) and its CLI dispatch."""

from __future__ import annotations

import pytest

from beril_cli import auth_store, ov_cmd
from beril_cli.cli import main
from beril_cli.ov_client import OvLinkError


@pytest.fixture
def tmp_auth(tmp_path, monkeypatch):
    """Redirect auth_store's on-disk location into tmp_path."""
    auth_dir = tmp_path / ".beril"
    auth_path = auth_dir / "auth.json"
    monkeypatch.setattr(auth_store, "AUTH_DIR", auth_dir)
    monkeypatch.setattr(auth_store, "AUTH_PATH", auth_path)
    return auth_path


def _login(*, ov=False):
    """Seed a stored BERIL login, optionally already OV-linked."""
    auth_store.save(
        token="beril_abc",
        base_url="https://srv.example.test",
        orcid_id="0000-0001-2345-6789",
        display_name="Alice",
        ov_url="https://srv.example.test/ov" if ov else None,
        ov_user_key="ov_key_1234" if ov else None,
    )


# ---------------------------------------------------------------------------
# beril ov setup
# ---------------------------------------------------------------------------


class TestOvSetup:
    def test_setup_requires_login(self, tmp_auth, capsys):
        rc = main(["ov", "setup"])
        assert rc == 1
        assert "Not logged in" in capsys.readouterr().err

    def test_setup_links_and_caches(self, tmp_auth, monkeypatch, capsys):
        _login(ov=False)

        def _fake(base_url, token, *, regenerate=False):
            assert base_url == "https://srv.example.test"
            assert token == "beril_abc"
            assert regenerate is False
            return ("https://srv.example.test/ov", "fresh_key_9999")

        monkeypatch.setattr(ov_cmd, "fetch_ov_credential", _fake)
        rc = main(["ov", "setup"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "linked" in out
        assert "fresh_key_9999" not in out  # masked

        record = auth_store.load()
        assert record.ov_user_key == "fresh_key_9999"
        # BERIL identity is preserved, not clobbered.
        assert record.token == "beril_abc"
        assert record.orcid_id == "0000-0001-2345-6789"

    def test_setup_regenerate_passes_flag(self, tmp_auth, monkeypatch, capsys):
        _login(ov=True)
        seen = {}

        def _fake(base_url, token, *, regenerate=False):
            seen["regenerate"] = regenerate
            return ("https://srv.example.test/ov", "rotated_key")

        monkeypatch.setattr(ov_cmd, "fetch_ov_credential", _fake)
        rc = main(["ov", "setup", "--regenerate"])
        assert rc == 0
        assert seen["regenerate"] is True
        assert "regenerated" in capsys.readouterr().out
        assert auth_store.load().ov_user_key == "rotated_key"

    def test_setup_409_points_at_regenerate(self, tmp_auth, monkeypatch, capsys):
        _login(ov=False)

        def _fake(base_url, token, *, regenerate=False):
            raise OvLinkError("already exists", needs_regenerate=True)

        monkeypatch.setattr(ov_cmd, "fetch_ov_credential", _fake)
        rc = main(["ov", "setup"])
        err = capsys.readouterr().err
        assert rc == 1
        assert "--regenerate" in err
        # Nothing cached on failure.
        assert auth_store.load().ov_user_key is None

    def test_setup_generic_failure_returns_1(self, tmp_auth, monkeypatch, capsys):
        _login(ov=False)

        def _fake(base_url, token, *, regenerate=False):
            raise OvLinkError("could not reach OpenViking.")

        monkeypatch.setattr(ov_cmd, "fetch_ov_credential", _fake)
        rc = main(["ov", "setup"])
        assert rc == 1
        assert "could not reach" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# beril ov status
# ---------------------------------------------------------------------------


class TestOvStatus:
    def test_status_requires_login(self, tmp_auth, capsys):
        rc = main(["ov", "status"])
        assert rc == 1
        assert "Not logged in" in capsys.readouterr().err

    def test_status_when_unlinked(self, tmp_auth, capsys):
        _login(ov=False)
        rc = main(["ov", "status"])
        assert rc == 1
        assert "not linked" in capsys.readouterr().out.lower()

    def test_status_prints_masked_key_and_health(self, tmp_auth, monkeypatch, capsys):
        _login(ov=True)
        monkeypatch.setattr(ov_cmd, "ov_health", lambda b, t: {"status": "ok"})
        rc = main(["ov", "status"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "https://srv.example.test/ov" in out
        assert "ok" in out
        # Full key never printed.
        assert "ov_key_1234" not in out

    def test_status_survives_health_probe_failure(self, tmp_auth, monkeypatch, capsys):
        _login(ov=True)

        def _boom(base_url, token):
            raise OvLinkError("unreachable")

        monkeypatch.setattr(ov_cmd, "ov_health", _boom)
        rc = main(["ov", "status"])
        out = capsys.readouterr().out
        assert rc == 0  # health failure must not fail status
        assert "unknown" in out


# ---------------------------------------------------------------------------
# beril ov print-env
# ---------------------------------------------------------------------------


class TestOvPrintEnv:
    def test_print_env_when_unlinked_fails(self, tmp_auth, capsys):
        _login(ov=False)
        rc = main(["ov", "print-env"])
        assert rc == 1
        assert "not linked" in capsys.readouterr().err.lower()

    def test_print_env_emits_valid_lines(self, tmp_auth, capsys):
        _login(ov=True)
        rc = main(["ov", "print-env"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "OPENVIKING_URL=https://srv.example.test/ov" in out
        assert "OPENVIKING_API_KEY=ov_key_1234" in out
        # Parseable as KEY=value lines.
        for line in out.strip().splitlines():
            assert "=" in line and line.split("=", 1)[0].isupper()
