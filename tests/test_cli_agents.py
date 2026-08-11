"""Tests for the supported-agent list shared by the CLI parser, setup, and doctor."""

from __future__ import annotations


import pytest

from beril_cli import cli, config, doctor


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
        config.SUPPORTED_AGENTS.append("rogue-agent")  # type: ignore[attr-defined]


# ── config.launch_argv ─────────────────────────────────


def test_claude_gets_the_opus_pin():
    assert config.launch_argv("claude", "/berdl_start") == [
        "claude",
        "--model",
        "opus",
        "/berdl_start",
    ]


@pytest.mark.parametrize("agent", ["codex", "gemini", "omp"])
def test_non_claude_agents_never_get_the_opus_pin(agent):
    """`--model opus` is Anthropic-specific and must not leak to other agents."""
    assert config.launch_argv(agent, "/berdl_start") == [agent, "/berdl_start"]


def test_explicit_model_is_not_overridden():
    """A caller-supplied --model wins over the Claude default."""
    argv = config.launch_argv("claude", "--model", "sonnet", "/berdl_start")
    assert argv == ["claude", "--model", "sonnet", "/berdl_start"]
    assert "opus" not in argv


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


def _agent_row(capsys) -> str:
    """Return the 'Agent CLIs' line from doctor's output."""
    lines = [ln for ln in capsys.readouterr().out.splitlines() if "Agent CLIs" in ln]
    assert lines, "doctor printed no Agent CLIs row"
    return lines[0]


def test_doctor_passes_when_only_omp_is_installed(monkeypatch, capsys):
    """omp alone satisfies the agent check, and is named in the row."""
    monkeypatch.setattr(
        doctor.shutil,
        "which",
        lambda name: "/usr/local/bin/omp" if name == "omp" else None,
    )
    doctor.run_doctor()
    row = _agent_row(capsys)
    assert "PASS" in row
    assert "omp" in row
    assert "claude" not in row


def test_doctor_warns_and_names_omp_when_nothing_installed(monkeypatch, capsys):
    """The 'none found' hint must name omp so users know it is an option."""
    monkeypatch.setattr(doctor.shutil, "which", lambda _name: None)
    doctor.run_doctor()
    row = _agent_row(capsys)
    assert "WARN" in row
    assert "omp" in row


# ── setup_cmd.py launch flags ──────────────────────────


def _fake_repo(tmp_path, monkeypatch):
    """Minimal repo `run_start` will accept: PROJECT.md marker plus a .env."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "PROJECT.md").write_text("")
    (repo / ".env").write_text("")
    monkeypatch.chdir(repo)
    return repo


@pytest.mark.parametrize("agent", ["codex", "gemini", "omp"])
def test_start_does_not_pass_opus_to_non_claude(tmp_path, monkeypatch, agent):
    """End-to-end through run_start: non-Claude agents get a clean argv.

    Regression guard for the real bug: `--model opus` used to be appended
    regardless of which agent was launched.
    """
    from beril_cli import start

    _fake_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(start.shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    monkeypatch.setattr(start, "_checkout_release", lambda *_a, **_kw: 0)
    monkeypatch.setattr(start, "print_jupyterhub_path_hint", lambda *_a: None)

    captured: dict = {}
    monkeypatch.setattr(start.os, "execvp", lambda _b, argv: captured.update(argv=argv))

    start.run_start(agent=agent)

    assert captured["argv"] == [agent, "/berdl_start"]


def test_start_does_pass_opus_to_claude(tmp_path, monkeypatch):
    """The Claude path keeps its Opus pin."""
    from beril_cli import start

    _fake_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(start.shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    monkeypatch.setattr(start, "_checkout_release", lambda *_a, **_kw: 0)
    monkeypatch.setattr(start, "print_jupyterhub_path_hint", lambda *_a: None)
    monkeypatch.setattr(start, "get_vertex_config", lambda: {})

    captured: dict = {}
    monkeypatch.setattr(start.os, "execvp", lambda _b, argv: captured.update(argv=argv))

    start.run_start(agent="claude")

    assert captured["argv"] == ["claude", "--model", "opus", "/berdl_start"]


# ── shared-list wiring ─────────────────────────────────


def test_doctor_probes_exactly_the_shared_agent_list(monkeypatch):
    """doctor must read the shared list, not a private copy.

    Swapping SUPPORTED_AGENTS for a sentinel proves doctor actually consults
    it: a hardcoded copy would probe the real names instead.
    """
    monkeypatch.setattr(config, "SUPPORTED_AGENTS", ("sentinel-a", "sentinel-b"))
    probed: list[str] = []

    def fake_which(name):
        probed.append(name)
        return None

    monkeypatch.setattr(doctor.shutil, "which", fake_which)
    doctor.run_doctor()

    assert "sentinel-a" in probed and "sentinel-b" in probed
    assert "claude" not in probed


def test_cli_choices_track_the_shared_agent_list(monkeypatch):
    """The parser's --agent choices come from the shared list."""
    monkeypatch.setattr(config, "SUPPORTED_AGENTS", ("sentinel-only",))
    parser = cli.build_parser()
    assert parser.parse_args(["start", "--agent", "sentinel-only"]).agent == "sentinel-only"
    with pytest.raises(SystemExit):
        parser.parse_args(["start", "--agent", "claude"])
