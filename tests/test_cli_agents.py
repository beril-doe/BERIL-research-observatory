"""Tests for the supported-agent list shared by the CLI parser, setup, and doctor."""

from __future__ import annotations

import inspect

import pytest

from beril_cli import cli, config, doctor, setup_cmd


# ── config.SUPPORTED_AGENTS ────────────────────────────


def test_omp_is_supported():
    """omp is launchable alongside the other agents."""
    assert "omp" in config.SUPPORTED_AGENTS


def test_default_agent_is_in_supported_list():
    """The fallback agent must itself be launchable."""
    assert config.DEFAULT_AGENT in config.SUPPORTED_AGENTS


def test_supported_agents_is_immutable():
    """A tuple, so callers cannot mutate the shared list in place."""
    assert isinstance(config.SUPPORTED_AGENTS, tuple)


# ── cli.py argument parsing ────────────────────────────


@pytest.mark.parametrize("agent", config.SUPPORTED_AGENTS)
def test_start_parser_accepts_every_supported_agent(agent):
    """`beril start --agent X` parses for every agent we claim to support."""
    args = cli.build_parser().parse_args(["start", "--agent", agent])
    assert args.agent == agent


def test_start_parser_rejects_unknown_agent():
    """An agent outside the list is a parse error, not a late failure."""
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["start", "--agent", "definitely-not-an-agent"])


# ── doctor.py ──────────────────────────────────────────


def test_doctor_detects_omp(monkeypatch, capsys):
    """doctor reports omp when it is the only agent on PATH."""
    monkeypatch.setattr(
        doctor.shutil,
        "which",
        lambda name: "/usr/local/bin/omp" if name == "omp" else None,
    )
    doctor.run_doctor()
    out = capsys.readouterr().out
    assert "omp" in out


def test_doctor_lists_omp_when_no_agent_found(monkeypatch, capsys):
    """The 'none found' hint must name omp, so users know it is an option."""
    monkeypatch.setattr(doctor.shutil, "which", lambda _name: None)
    doctor.run_doctor()
    assert "omp" in capsys.readouterr().out


# ── setup_cmd.py launch flags ──────────────────────────


def test_setup_cmd_guards_the_opus_model_pin():
    """`--model opus` is Anthropic-specific and must not leak to other agents.

    Regression guard: setup_cmd previously passed it unconditionally, so
    launching codex/gemini/omp from `beril setup` handed them a flag they do
    not understand. start.py already gated this; setup_cmd did not.
    """
    src = inspect.getsource(setup_cmd.run_setup)
    assert 'if chosen == "claude" else []' in src, (
        "setup_cmd must not pass --model opus unconditionally"
    )


def test_start_guards_the_opus_model_pin():
    """The same gate exists on the `beril start` path."""
    from beril_cli import start

    src = inspect.getsource(start.run_start)
    assert 'agent == "claude"' in src


# ── shared-list wiring ─────────────────────────────────


@pytest.mark.parametrize("module", [setup_cmd, doctor, cli])
def test_modules_use_the_shared_agent_list(module):
    """No module may keep a private copy of the agent list."""
    src = inspect.getsource(module)
    assert "SUPPORTED_AGENTS" in src, f"{module.__name__} has its own agent list"
