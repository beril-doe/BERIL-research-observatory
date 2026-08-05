"""Tests for the `beril setup` wizard (`beril_cli.setup_cmd`).

Covers the wizard's deterministic helpers — the .env parser/writer, repo-root
discovery, the input prompts, the best-effort BERIL login step, and the pure
branches of the jupyter-server-proxy installer. The full `run_setup` orchestrator
(subprocess-heavy, ends in `os.execvp`) is exercised through these units rather
than end-to-end.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from beril_cli import setup_cmd
from beril_cli.auth_store import AuthRecord


# ---------------------------------------------------------------------------
# _parse_env_file — minimal .env reader
# ---------------------------------------------------------------------------


class TestParseEnvFile:
    def test_missing_file_returns_empty(self, tmp_path):
        assert setup_cmd._parse_env_file(tmp_path / "nope.env") == {}

    def test_basic_key_values(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=1\nB=two\n")
        assert setup_cmd._parse_env_file(env) == {"A": "1", "B": "two"}

    def test_skips_comments_and_blank_lines(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("# a comment\n\nA=1\n   \n# another\nB=2\n")
        assert setup_cmd._parse_env_file(env) == {"A": "1", "B": "2"}

    def test_skips_lines_without_equals(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=1\ngarbage line\nB=2\n")
        assert setup_cmd._parse_env_file(env) == {"A": "1", "B": "2"}

    def test_strips_surrounding_quotes(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=\"double\"\nB='single'\nC=bare\n")
        assert setup_cmd._parse_env_file(env) == {
            "A": "double",
            "B": "single",
            "C": "bare",
        }

    def test_value_with_equals_sign_is_kept_whole(self, tmp_path):
        # Only the first `=` splits key from value — URLs / base64 with `=`
        # survive intact.
        env = tmp_path / ".env"
        env.write_text("URL=https://x/y?a=b&c=d\n")
        assert setup_cmd._parse_env_file(env) == {"URL": "https://x/y?a=b&c=d"}

    def test_whitespace_around_key_and_value_trimmed(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("  A =  1  \n")
        assert setup_cmd._parse_env_file(env) == {"A": "1"}


# ---------------------------------------------------------------------------
# _update_env_var — in-place key upsert
# ---------------------------------------------------------------------------


class TestUpdateEnvVar:
    def test_updates_existing_key_in_place(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=1\nB=2\nC=3\n")
        setup_cmd._update_env_var(env, "B", "changed")
        assert setup_cmd._parse_env_file(env) == {"A": "1", "B": "changed", "C": "3"}

    def test_appends_missing_key(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=1\n")
        setup_cmd._update_env_var(env, "NEW", "val")
        assert setup_cmd._parse_env_file(env) == {"A": "1", "NEW": "val"}

    def test_preserves_key_order_on_update(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=1\nB=2\nC=3\n")
        setup_cmd._update_env_var(env, "B", "9")
        assert env.read_text().splitlines() == ["A=1", "B=9", "C=3"]

    def test_only_first_match_is_updated(self, tmp_path):
        # A malformed file with a duplicate key updates only the first; the
        # second is left as-is (and _parse_env_file's last-wins would then read
        # the stale one — the guard is that update touches exactly one line).
        env = tmp_path / ".env"
        env.write_text("DUP=old\nDUP=old\n")
        setup_cmd._update_env_var(env, "DUP", "new")
        assert env.read_text().splitlines() == ["DUP=new", "DUP=old"]

    def test_appends_to_file_without_trailing_newline(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("A=1")  # no trailing newline
        setup_cmd._update_env_var(env, "B", "2")
        assert env.read_text() == "A=1\nB=2\n"

    def test_does_not_match_key_as_substring(self, tmp_path):
        # `TOKEN` must not be updated when asked to set `AUTH_TOKEN`: matching is
        # on the `KEY=` prefix, so a distinct key is appended, not overwritten.
        env = tmp_path / ".env"
        env.write_text("TOKEN=keepme\n")
        setup_cmd._update_env_var(env, "AUTH_TOKEN", "new")
        assert setup_cmd._parse_env_file(env) == {
            "TOKEN": "keepme",
            "AUTH_TOKEN": "new",
        }


# ---------------------------------------------------------------------------
# _find_repo_root — walk up for PROJECT.md
# ---------------------------------------------------------------------------


class TestFindRepoRoot:
    def test_finds_marker_in_cwd(self, tmp_path, monkeypatch):
        (tmp_path / "PROJECT.md").write_text("x")
        monkeypatch.chdir(tmp_path)
        assert setup_cmd._find_repo_root() == tmp_path

    def test_finds_marker_in_ancestor(self, tmp_path, monkeypatch):
        (tmp_path / "PROJECT.md").write_text("x")
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        monkeypatch.chdir(deep)
        assert setup_cmd._find_repo_root() == tmp_path

    def test_returns_none_when_absent(self, tmp_path, monkeypatch):
        # tmp_path has no PROJECT.md; walking to filesystem root finds none.
        # (Guards against a stray PROJECT.md somewhere above the real cwd by
        # using an isolated tmp tree.)
        deep = tmp_path / "x" / "y"
        deep.mkdir(parents=True)
        monkeypatch.chdir(deep)
        # Only assert None if no ancestor happens to carry the marker.
        result = setup_cmd._find_repo_root()
        assert result is None or (result / "PROJECT.md").exists()


# ---------------------------------------------------------------------------
# _confirm / _prompt — thin input() wrappers
# ---------------------------------------------------------------------------


class TestConfirm:
    @pytest.mark.parametrize(
        "answer,default,expected",
        [
            ("", True, True),      # empty accepts the default...
            ("", False, False),    # ...whichever it is
            ("y", False, True),
            ("yes", False, True),
            ("Y", False, True),
            ("  yes  ", False, True),  # trimmed + lowercased
            ("n", True, False),
            ("no", True, False),
            ("nope", True, False),     # anything not y/yes is False
            ("garbage", True, False),
        ],
    )
    def test_confirm(self, monkeypatch, answer, default, expected):
        monkeypatch.setattr("builtins.input", lambda _prompt="": answer)
        assert setup_cmd._confirm("q?", default=default) is expected


class TestPrompt:
    def test_returns_typed_answer(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _prompt="": "  typed  ")
        assert setup_cmd._prompt("q", default="def") == "typed"

    def test_empty_answer_falls_back_to_default(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _prompt="": "   ")
        assert setup_cmd._prompt("q", default="def") == "def"

    def test_no_default_and_empty_returns_empty(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _prompt="": "")
        assert setup_cmd._prompt("q") == ""


# ---------------------------------------------------------------------------
# _run_login_step — best-effort BERIL login inside setup
# ---------------------------------------------------------------------------


@pytest.fixture
def base_url(monkeypatch):
    """Pin the resolved BERIL base URL so the step never hits config/network."""
    monkeypatch.setattr(setup_cmd.config, "get_base_url", lambda: "https://beril.test")


@pytest.fixture
def tty(monkeypatch):
    """Force stdin to look like an interactive terminal."""
    fake = MagicMock()
    fake.isatty.return_value = True
    monkeypatch.setattr(setup_cmd.sys, "stdin", fake)


def _no_record(monkeypatch):
    monkeypatch.setattr(setup_cmd.auth_store, "load", lambda: None)


@pytest.mark.usefixtures("base_url")
class TestRunLoginStep:
    def test_skips_when_already_logged_in(self, monkeypatch):
        record = AuthRecord(
            token="t",
            base_url="https://beril.test",
            orcid_id="0000-0000-0000-0001",
            display_name="Ada",
        )
        monkeypatch.setattr(setup_cmd.auth_store, "load", lambda: record)
        called = MagicMock()
        monkeypatch.setattr(setup_cmd, "run_login", called)

        setup_cmd._run_login_step()

        # A logged-in user is never re-prompted or re-authenticated.
        called.assert_not_called()

    def test_skips_off_tty_without_prompting(self, monkeypatch):
        _no_record(monkeypatch)
        fake = MagicMock()
        fake.isatty.return_value = False
        monkeypatch.setattr(setup_cmd.sys, "stdin", fake)
        called = MagicMock()
        monkeypatch.setattr(setup_cmd, "run_login", called)
        # _confirm would call input() and hang off a TTY — assert we never reach it.
        monkeypatch.setattr(
            setup_cmd, "_confirm", MagicMock(side_effect=AssertionError("prompted off-TTY"))
        )

        setup_cmd._run_login_step()

        called.assert_not_called()

    def test_declined_does_not_log_in(self, monkeypatch, tty):
        _no_record(monkeypatch)
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: False)
        called = MagicMock()
        monkeypatch.setattr(setup_cmd, "run_login", called)

        setup_cmd._run_login_step()

        called.assert_not_called()

    def test_accepted_delegates_to_run_login(self, monkeypatch, tty):
        _no_record(monkeypatch)
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
        called = MagicMock(return_value=0)
        monkeypatch.setattr(setup_cmd, "run_login", called)

        setup_cmd._run_login_step()

        called.assert_called_once_with()

    def test_login_failure_is_not_fatal(self, monkeypatch, tty):
        # A non-zero run_login return (bad token, unreachable server) must not
        # raise — setup continues. The step swallows it after noting the failure.
        _no_record(monkeypatch)
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
        monkeypatch.setattr(setup_cmd, "run_login", MagicMock(return_value=1))

        setup_cmd._run_login_step()  # must not raise

    def test_login_interrupt_is_not_fatal(self, monkeypatch, tty):
        # Ctrl-C / EOF at the token prompt bubbles out of run_login; the step
        # catches it so setup can finish rather than aborting the whole wizard.
        _no_record(monkeypatch)
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
        monkeypatch.setattr(
            setup_cmd, "run_login", MagicMock(side_effect=KeyboardInterrupt)
        )

        setup_cmd._run_login_step()  # must not raise


# ---------------------------------------------------------------------------
# _install_server_proxy — pure/early-return branches
#
# The full install path shells out (pip, jupyter) and restarts the server, so we
# cover only the branches that return before any subprocess: dashboard-API
# unavailable, already-enabled, no interpreter found, and off-TTY refusal.
# ---------------------------------------------------------------------------


class TestInstallServerProxy:
    def test_returns_1_when_dashboard_api_unavailable(self, tmp_path, monkeypatch):
        # _dashboard_api returns (None, None, ()) when tools/dashboard.py can't
        # be imported — the installer must bail with 1, not crash.
        monkeypatch.setattr(setup_cmd, "_dashboard_api", lambda root: (None, None, ()))
        assert setup_cmd._install_server_proxy(tmp_path) == 1

    def test_returns_0_when_already_enabled(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            setup_cmd,
            "_dashboard_api",
            lambda root: (lambda: True, lambda: "/usr/bin/python", ("restart",)),
        )
        run = MagicMock()
        monkeypatch.setattr(setup_cmd.subprocess, "run", run)

        assert setup_cmd._install_server_proxy(tmp_path) == 0
        run.assert_not_called()  # nothing installed when already enabled

    def test_returns_1_when_no_jupyter_interpreter(self, tmp_path, monkeypatch):
        # proxy not enabled, but jupyter_python() can't locate the server's
        # interpreter → bail before installing.
        monkeypatch.setattr(
            setup_cmd,
            "_dashboard_api",
            lambda root: (lambda: False, lambda: None, ("restart",)),
        )
        run = MagicMock()
        monkeypatch.setattr(setup_cmd.subprocess, "run", run)

        assert setup_cmd._install_server_proxy(tmp_path) == 1
        run.assert_not_called()

    def test_refuses_off_tty_without_yes(self, tmp_path, monkeypatch):
        # Not enabled, interpreter found, but not a TTY and assume_yes=False →
        # refuse before running anything.
        monkeypatch.setattr(
            setup_cmd,
            "_dashboard_api",
            lambda root: (lambda: False, lambda: "/usr/bin/python", ("restart",)),
        )
        fake = MagicMock()
        fake.isatty.return_value = False
        monkeypatch.setattr(setup_cmd.sys, "stdin", fake)
        run = MagicMock()
        monkeypatch.setattr(setup_cmd.subprocess, "run", run)

        assert setup_cmd._install_server_proxy(tmp_path, assume_yes=False) == 1
        run.assert_not_called()
