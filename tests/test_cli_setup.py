"""Tests for the `beril setup` wizard's BERIL login step (`_run_login_step`).

The step is best-effort: setup must complete whether login is skipped, declined,
or fails, and it must never prompt (and hang) off a TTY. It also short-circuits
when a valid login already exists.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from beril_cli import setup_cmd
from beril_cli.auth_store import AuthRecord


@pytest.fixture(autouse=True)
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


def test_skips_when_already_logged_in(monkeypatch):
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


def test_skips_off_tty_without_prompting(monkeypatch):
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


def test_declined_does_not_log_in(monkeypatch, tty):
    _no_record(monkeypatch)
    monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: False)
    called = MagicMock()
    monkeypatch.setattr(setup_cmd, "run_login", called)

    setup_cmd._run_login_step()

    called.assert_not_called()


def test_accepted_delegates_to_run_login(monkeypatch, tty):
    _no_record(monkeypatch)
    monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
    called = MagicMock(return_value=0)
    monkeypatch.setattr(setup_cmd, "run_login", called)

    setup_cmd._run_login_step()

    called.assert_called_once_with()


def test_login_failure_is_not_fatal(monkeypatch, tty):
    # A non-zero run_login return (bad token, unreachable server) must not raise
    # — setup continues. The step swallows it after noting the failure.
    _no_record(monkeypatch)
    monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
    monkeypatch.setattr(setup_cmd, "run_login", MagicMock(return_value=1))

    setup_cmd._run_login_step()  # must not raise


def test_login_interrupt_is_not_fatal(monkeypatch, tty):
    # Ctrl-C / EOF at the token prompt bubbles out of run_login; the step
    # catches it so setup can finish rather than aborting the whole wizard.
    _no_record(monkeypatch)
    monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
    monkeypatch.setattr(
        setup_cmd, "run_login", MagicMock(side_effect=KeyboardInterrupt)
    )

    setup_cmd._run_login_step()  # must not raise
