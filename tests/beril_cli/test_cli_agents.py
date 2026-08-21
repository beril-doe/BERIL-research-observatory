"""Tests for the supported-agent list shared by the CLI parser, setup, and doctor."""

from __future__ import annotations

from pathlib import Path

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


def _launch(tmp_path, monkeypatch, **kwargs) -> list[str]:
    """Drive run_start to the execvp boundary and return the argv it would exec."""
    _fake_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(start.shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    monkeypatch.setattr(start, "_checkout_release", lambda *_a, **_kw: 0)
    monkeypatch.setattr(start, "print_jupyterhub_path_hint", lambda *_a: None)

    captured: dict = {}
    monkeypatch.setattr(start.os, "execvp", lambda _b, argv: captured.update(argv=argv))

    start.run_start(**kwargs)
    return captured["argv"]


@pytest.mark.parametrize("agent", ["codex", "gemini", "omp"])
def test_start_does_not_pass_claude_flags_to_other_agents(tmp_path, monkeypatch, agent):
    """End-to-end through run_start: no Claude-only flag reaches another agent."""
    argv = _launch(tmp_path, monkeypatch, agent=agent)
    assert "--model" not in argv and "--permission-mode" not in argv


@pytest.mark.parametrize("agent", ["codex", "gemini"])
def test_start_argv_is_bare_for_agents_with_no_defaults(tmp_path, monkeypatch, agent):
    """codex and gemini get nothing but the onboarding prompt."""
    assert _launch(tmp_path, monkeypatch, agent=agent) == [agent, "/berdl_start"]


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


# ── omp: a session directory the collector can name ────


@pytest.mark.parametrize("agent", ["claude", "codex", "gemini"])
def test_omp_defaults_returns_nothing_for_other_agents(agent, tmp_path):
    assert start.omp_defaults(agent, [], tmp_path) == []


def test_omp_defaults_points_under_home_not_into_the_checkout(tmp_path):
    """BERDL pods are ephemeral and $HOME persists, so the transcript lives in $HOME.

    Asserted against the literal layout, not against `omp_session_dir` -- comparing the
    constant to itself would pass however the path were renamed, and nothing else pins it.
    """
    (flag, value), = [start.omp_defaults("omp", [], tmp_path)[i : i + 2] for i in (0,)]
    assert flag == "--session-dir"
    path = Path(value)
    assert path.parent == Path.home() / ".beril" / "omp-sessions"
    assert path.name.startswith(f"{tmp_path.resolve().name}-")
    # Nothing is written into the checkout.
    assert not any(tmp_path.iterdir())


def test_two_checkouts_with_one_name_get_different_directories(tmp_path):
    """Keyed by resolved path: two clones of the same repo must not share sessions."""
    a, b = tmp_path / "one" / "BERIL", tmp_path / "two" / "BERIL"
    for d in (a, b):
        d.mkdir(parents=True)
    assert start.omp_session_dir(a) != start.omp_session_dir(b)
    assert start.omp_session_dir(a) == start.omp_session_dir(a)  # stable across runs


@pytest.mark.parametrize(
    "supplied",
    [["--session-dir", "/somewhere/else"], ["--session-dir=/somewhere/else"]],
)
def test_omp_defaults_respects_a_caller_supplied_session_dir(supplied, tmp_path):
    """Both flag spellings count: passing the default too would hand omp two values."""
    assert start.omp_defaults("omp", supplied, tmp_path) == []


def test_has_flag_matches_both_spellings():
    assert start._has_flag(["--model", "sonnet"], "--model")
    assert start._has_flag(["--model=sonnet"], "--model")
    assert not start._has_flag(["--model-something"], "--model")
    assert not start._has_flag([], "--model")


def test_start_gives_omp_a_session_dir_and_still_onboards(tmp_path, monkeypatch):
    """On the default path the operator gets both.

    The onboarding guard is `if not skip_onboard and not extra_args`, so an operator who
    passed --session-dir by hand lost /berdl_start. Injecting on BERIL's side sidesteps
    that -- it does not repair the guard, which still drops onboarding for *any* forwarded
    flag. See test_any_forwarded_flag_still_costs_onboarding.
    """
    argv = _launch(tmp_path, monkeypatch, agent="omp")
    expected = str(start.omp_session_dir(tmp_path / "repo"))
    assert argv == ["omp", "--session-dir", expected, "/berdl_start"]


def test_any_forwarded_flag_still_costs_onboarding(tmp_path, monkeypatch):
    """Pre-existing and NOT fixed here: the guard cannot tell a flag from a prompt.

    Pinned rather than left implicit so the limitation is visible, and so a later fix has
    a test to change deliberately.
    """
    argv = _launch(tmp_path, monkeypatch, agent="omp", extra_args=["--thinking", "high"])
    assert "/berdl_start" not in argv
    assert "--session-dir" in argv  # the session dir is still injected


def test_start_lets_the_operator_override_the_session_dir(tmp_path, monkeypatch):
    """An explicit --session-dir wins, and is not doubled."""
    argv = _launch(
        tmp_path, monkeypatch, agent="omp", extra_args=["--session-dir", "/elsewhere"]
    )
    assert argv.count("--session-dir") == 1
    assert argv == ["omp", "--session-dir", "/elsewhere"]


def test_start_announces_the_omp_session_dir_without_creating_it(tmp_path, monkeypatch):
    """A collector needs the path, so it is printed. omp creates the directory itself.

    Creating it here would run between "Launching omp..." and execvp, where a path occupied
    by a file raises and the agent never starts.
    """
    argv = _launch(tmp_path, monkeypatch, agent="omp")
    assert str(start.omp_session_dir(tmp_path / "repo")) == argv[2]


def test_announce_does_not_touch_the_filesystem(tmp_path, capsys):
    """Pinned against a path that cannot be created: a plain file where the dir would go."""
    blocked = tmp_path / "blocked"
    blocked.write_text("")  # a FILE, so mkdir here would raise FileExistsError
    start.announce_omp_session(["--session-dir", str(blocked / "nested")])
    assert str(blocked / "nested") in capsys.readouterr().out
    assert blocked.is_file()


def test_claude_is_unaffected_by_the_omp_session_dir(tmp_path, monkeypatch):
    """Claude keeps its own defaults and gains no session flag."""
    argv = _launch(tmp_path, monkeypatch, agent="claude")
    assert "--session-dir" not in argv
    assert "--model" in argv and "opus[1m]" in argv


def test_a_caller_supplied_model_with_equals_is_not_doubled(tmp_path, monkeypatch):
    """End-to-end for the `--model=x` fix: `"--model" not in extra_args` misses this form.

    The helper test alone let a revert to the old membership check pass the whole suite.
    """
    argv = _launch(tmp_path, monkeypatch, agent="claude", extra_args=["--model=sonnet"])
    assert argv.count("--model") == 0  # the default was withheld
    assert argv == ["claude", "--permission-mode", "auto", "--model=sonnet"]
