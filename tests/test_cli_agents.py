"""Tests for the supported-agent list shared by the CLI parser, setup, and doctor."""

from __future__ import annotations

import pytest

from beril_cli import cli, config, doctor, start


# ── config.SUPPORTED_AGENTS ────────────────────────────


def test_omp_is_supported():
    """omp is launchable alongside the other agents."""
    assert "omp" in config.SUPPORTED_AGENTS


def test_default_agent_is_in_supported_list():
    """The fallback agent must itself be launchable."""
    assert config.DEFAULT_AGENT in config.SUPPORTED_AGENTS


def test_supported_agents_cannot_be_mutated_by_callers():
    """A caller cannot append to the shared list and affect everyone else."""
    with pytest.raises((AttributeError, TypeError)):
        config.SUPPORTED_AGENTS.append("rogue")  # type: ignore[attr-defined]


# ── config.get_default_agent ───────────────────────────


def test_get_default_agent_falls_back_when_unconfigured(tmp_path, monkeypatch):
    """With no config file on disk, the shared DEFAULT_AGENT is used."""
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "absent.toml")
    assert config.get_default_agent() == config.DEFAULT_AGENT


def test_get_default_agent_reads_configured_agent(tmp_path, monkeypatch):
    """An agent pinned in config.toml wins over the fallback."""
    cfg = tmp_path / "config.toml"
    cfg.write_text('[defaults]\nagent = "omp"\n')
    monkeypatch.setattr(config, "CONFIG_PATH", cfg)
    assert config.get_default_agent() == "omp"


def test_get_default_agent_falls_back_when_section_absent(tmp_path, monkeypatch):
    """A config.toml without a [defaults] section still yields the fallback."""
    cfg = tmp_path / "config.toml"
    cfg.write_text('[user]\nname = "someone"\n')
    monkeypatch.setattr(config, "CONFIG_PATH", cfg)
    assert config.get_default_agent() == config.DEFAULT_AGENT


# ── claude_defaults: Claude-only flags ─────────────────


@pytest.mark.parametrize("agent", ["codex", "gemini", "omp"])
def test_claude_defaults_returns_nothing_for_other_agents(agent):
    assert start.claude_defaults(agent, []) == []


def test_claude_defaults_pins_opus_for_claude():
    flags = start.claude_defaults("claude", [])
    assert "--model" in flags and "opus[1m]" in flags


def test_claude_defaults_respects_caller_supplied_model():
    flags = start.claude_defaults("claude", ["--model", "sonnet"])
    assert "--model" not in flags


# ── cli.py argument parsing ────────────────────────────


@pytest.mark.parametrize("agent", config.SUPPORTED_AGENTS)
def test_start_parser_accepts_every_supported_agent(agent):
    """`beril start --agent X` parses for every agent we claim to support."""
    assert cli.build_parser().parse_args(["start", "--agent", agent]).agent == agent


def test_start_parser_rejects_unknown_agent():
    """An agent outside the list is a parse error, not a late failure."""
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["start", "--agent", "definitely-not-an-agent"])


def test_cli_choices_track_the_shared_agent_list(monkeypatch):
    """The parser's --agent choices come from the shared list, not a copy."""
    monkeypatch.setattr(config, "SUPPORTED_AGENTS", ("sentinel-only",))
    parser = cli.build_parser()
    assert parser.parse_args(["start", "--agent", "sentinel-only"]).agent == "sentinel-only"
    with pytest.raises(SystemExit):
        parser.parse_args(["start", "--agent", "claude"])


# ── doctor.py ──────────────────────────────────────────


def _agent_row(capsys) -> str:
    lines = [ln for ln in capsys.readouterr().out.splitlines() if "Agent CLIs" in ln]
    assert lines, "doctor printed no Agent CLIs row"
    return lines[0]


def test_doctor_passes_when_only_omp_is_installed(monkeypatch, capsys):
    """omp alone satisfies the agent check and is named in the row."""
    monkeypatch.setattr(
        doctor.shutil, "which", lambda n: "/usr/local/bin/omp" if n == "omp" else None
    )
    doctor.run_doctor()
    row = _agent_row(capsys)
    assert "PASS" in row and "omp" in row


def test_doctor_warns_and_names_omp_when_nothing_installed(monkeypatch, capsys):
    """The 'none found' hint must name omp so users know it is an option."""
    monkeypatch.setattr(doctor.shutil, "which", lambda _n: None)
    doctor.run_doctor()
    row = _agent_row(capsys)
    assert "WARN" in row and "omp" in row


def test_doctor_probes_exactly_the_shared_agent_list(monkeypatch):
    """Swapping in a sentinel proves doctor consults the shared list."""
    monkeypatch.setattr(config, "SUPPORTED_AGENTS", ("sentinel-a", "sentinel-b"))
    probed: list[str] = []

    def fake_which(name):
        probed.append(name)
        return None

    monkeypatch.setattr(doctor.shutil, "which", fake_which)
    doctor.run_doctor()

    assert "sentinel-a" in probed and "sentinel-b" in probed
    assert "claude" not in probed


# ── the launch argv actually handed to execvp ──────────


def _fake_repo(tmp_path, monkeypatch):
    """Minimal repo run_start accepts: PROJECT.md marker plus a .env."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "PROJECT.md").write_text("")
    (repo / ".env").write_text("")
    monkeypatch.chdir(repo)
    return repo


@pytest.mark.parametrize("agent", ["codex", "gemini", "omp"])
def test_start_does_not_pass_claude_flags_to_other_agents(tmp_path, monkeypatch, agent):
    """End-to-end through run_start: non-Claude agents get a clean argv."""
    _fake_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(start.shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    monkeypatch.setattr(start, "_checkout_release", lambda *_a, **_kw: 0)
    monkeypatch.setattr(start, "print_jupyterhub_path_hint", lambda *_a: None)

    captured: dict = {}
    monkeypatch.setattr(start.os, "execvp", lambda _b, argv: captured.update(argv=argv))

    start.run_start(agent=agent)

    assert captured["argv"] == [agent, "/berdl_start"]


def test_setup_launch_does_not_pass_claude_flags_to_other_agents():
    """Regression: setup used `claude_defaults(chosen, []) or ["--model", "opus"]`.

    `claude_defaults` returns [] for non-Claude agents, and `[] or [...]`
    evaluates to the right-hand side, so the fallback reinstated exactly the
    flag the function exists to withhold. codex/gemini/omp were launched with
    `--model opus`.
    """
    for agent in ("codex", "gemini", "omp"):
        flags = start.claude_defaults(agent, [])
        argv = [agent, *flags, "/berdl_start"]
        assert argv == [agent, "/berdl_start"], f"{agent} got Claude-only flags"

    claude_argv = ["claude", *start.claude_defaults("claude", []), "/berdl_start"]
    assert "--model" in claude_argv and "opus[1m]" in claude_argv
