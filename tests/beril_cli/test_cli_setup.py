"""Tests for the `beril setup` wizard (`beril_cli.setup_cmd`).

Covers the wizard's deterministic helpers — the .env parser/writer, repo-root
discovery, the input prompts, the best-effort BERIL login step, and the pure
branches of the jupyter-server-proxy installer — and the `run_setup` orchestrator
itself, driven end-to-end with its external boundaries (subprocess, config,
identity detection, proxy install, the final launch) mocked at the module edge.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from beril_cli import setup_cmd, start
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


# ---------------------------------------------------------------------------
# run_setup — the wizard orchestrator, driven end-to-end
#
# External boundaries are mocked at the module edge: subprocess (git clone,
# detection script, gh, bootstrap), config load/save, identity detection, the
# jupyter-proxy installer, and the final launch. Step 2's real .env file logic
# runs against a tmp_path repo so the parser/writer are exercised in situ.
# ---------------------------------------------------------------------------


def _completed(returncode=0, stdout=""):
    """A stand-in for subprocess.CompletedProcess."""
    cp = MagicMock()
    cp.returncode = returncode
    cp.stdout = stdout
    return cp


@pytest.fixture
def repo(tmp_path):
    """A repo root with the PROJECT.md marker and a .env.example."""
    (tmp_path / "PROJECT.md").write_text("x")
    (tmp_path / ".env.example").write_text("KBASE_AUTH_TOKEN=YOUR_AUTH_TOKEN_HERE\n")
    return tmp_path


@pytest.fixture
def happy_setup(monkeypatch, repo):
    """Mock every external boundary of run_setup for a clean off-cluster run.

    Individual tests override pieces of this to drive a specific branch. Returns
    a namespace of the key mocks/paths so assertions can reach them.

    Defaults chosen so the wizard runs start-to-finish and returns 0 without
    launching: repo is found (no clone), no detect script (off-cluster), venv
    already present, gh absent, no coding agent detected (so no launch prompt /
    execvp), no Vertex creds.
    """
    monkeypatch.setattr(setup_cmd, "_find_repo_root", lambda: repo)
    monkeypatch.setattr(setup_cmd, "_run_login_step", MagicMock())
    monkeypatch.setattr(setup_cmd, "_install_server_proxy", MagicMock(return_value=0))
    monkeypatch.setattr(setup_cmd, "detect_user_identity", lambda: {})
    monkeypatch.setattr(setup_cmd, "print_jupyterhub_path_hint", MagicMock())
    monkeypatch.setattr(setup_cmd.config, "load", lambda: {})
    saved: dict = {}
    monkeypatch.setattr(setup_cmd.config, "save", lambda cfg: saved.update({"cfg": cfg}))
    monkeypatch.setattr(setup_cmd.config, "CONFIG_PATH", repo / "config.toml")

    # No env vars to sync, and _prompt/_confirm never asked to launch.
    for key in ("KBASE_AUTH_TOKEN", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_ENDPOINT_URL"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(setup_cmd, "_prompt", lambda q, default="": default)
    monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)

    # venv exists → no bootstrap; no coding agent on PATH → no launch/execvp.
    (repo / ".venv-berdl").mkdir()
    monkeypatch.setattr(setup_cmd.shutil, "which", lambda name: None)

    # Default: every subprocess call succeeds. Tests can override.
    run = MagicMock(return_value=_completed(0))
    monkeypatch.setattr(setup_cmd.subprocess, "run", run)

    ns = MagicMock()
    ns.repo = repo
    ns.saved = saved
    ns.run = run
    return ns


_VERTEX_ENV_KEYS = (
    "CLAUDE_CODE_USE_VERTEX",
    "CLOUD_ML_REGION",
    "ANTHROPIC_VERTEX_PROJECT_ID",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "VERTEX_REGION_CLAUDE_HAIKU_4_5",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
)


class TestRunSetupOrchestrator:
    @pytest.fixture(autouse=True)
    def _isolate_vertex_env(self, monkeypatch):
        # run_setup sets Vertex vars on os.environ just before execvp. With
        # execvp mocked (no process replacement) they would leak into later
        # tests, so drop them for each test and let monkeypatch restore state.
        for key in _VERTEX_ENV_KEYS:
            monkeypatch.delenv(key, raising=False)

    def test_happy_path_returns_0_and_saves_config(self, happy_setup):
        rc = setup_cmd.run_setup()
        assert rc == 0
        # Config was persisted with the resolved default agent.
        assert "cfg" in happy_setup.saved
        assert happy_setup.saved["cfg"]["defaults"]["agent"] == "claude"

    def test_creates_env_from_example(self, happy_setup):
        env_path = happy_setup.repo / ".env"
        assert not env_path.exists()
        setup_cmd.run_setup()
        # .env was created by copying .env.example.
        assert env_path.exists()
        assert "KBASE_AUTH_TOKEN" in env_path.read_text()

    def test_syncs_env_token_into_dotenv(self, happy_setup, monkeypatch):
        monkeypatch.setenv("KBASE_AUTH_TOKEN", "live-token-123")
        setup_cmd.run_setup()
        parsed = setup_cmd._parse_env_file(happy_setup.repo / ".env")
        # The live environment token overwrote the .env.example placeholder.
        assert parsed["KBASE_AUTH_TOKEN"] == "live-token-123"

    def test_prompts_for_token_when_placeholder(self, happy_setup, monkeypatch):
        # No env token, .env carries the placeholder → wizard prompts, and a
        # typed token lands in .env.
        monkeypatch.setattr(setup_cmd, "_prompt", lambda q, default="": "typed-token")
        setup_cmd.run_setup()
        parsed = setup_cmd._parse_env_file(happy_setup.repo / ".env")
        assert parsed["KBASE_AUTH_TOKEN"] == "typed-token"

    def test_runs_login_step(self, happy_setup):
        setup_cmd.run_setup()
        setup_cmd._run_login_step.assert_called_once()

    def test_repo_not_found_and_declined_returns_1(self, monkeypatch):
        monkeypatch.setattr(setup_cmd, "_find_repo_root", lambda: None)
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: False)
        run = MagicMock()
        monkeypatch.setattr(setup_cmd.subprocess, "run", run)

        assert setup_cmd.run_setup() == 1
        # Declining the clone means git is never invoked.
        run.assert_not_called()

    def test_repo_not_found_clone_failure_returns_1(self, monkeypatch, tmp_path):
        monkeypatch.setattr(setup_cmd, "_find_repo_root", lambda: None)
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
        monkeypatch.setattr(
            setup_cmd.subprocess, "run", lambda *a, **k: _completed(returncode=1)
        )

        assert setup_cmd.run_setup() == 1

    def test_off_cluster_bootstrap_failure_returns_1(self, happy_setup, monkeypatch):
        # No venv, a bootstrap script present, and bootstrap exits non-zero →
        # run_setup bails with 1 before reaching later steps.
        import shutil as _shutil

        _shutil.rmtree(happy_setup.repo / ".venv-berdl")
        (happy_setup.repo / "scripts").mkdir()
        (happy_setup.repo / "scripts" / "bootstrap_client.sh").write_text("#!/bin/sh\n")

        def fake_run(cmd, *a, **k):
            if cmd[0] == "bash":  # the bootstrap invocation
                return _completed(returncode=1)
            return _completed(0)

        monkeypatch.setattr(setup_cmd.subprocess, "run", fake_run)
        assert setup_cmd.run_setup() == 1

    def test_on_cluster_skips_bootstrap(self, happy_setup, monkeypatch):
        # A detection script reporting on-cluster means the venv/bootstrap step
        # is skipped entirely — bootstrap is never invoked even without a venv.
        import shutil as _shutil

        _shutil.rmtree(happy_setup.repo / ".venv-berdl")
        (happy_setup.repo / "scripts").mkdir()
        (happy_setup.repo / "scripts" / "detect_berdl_environment.py").write_text("x")
        (happy_setup.repo / "scripts" / "bootstrap_client.sh").write_text("#!/bin/sh\n")

        calls = []

        def fake_run(cmd, *a, **k):
            calls.append(cmd)
            if cmd and cmd[-1].endswith("detect_berdl_environment.py"):
                return _completed(0, stdout='{"location": "on-cluster"}')
            return _completed(0)

        monkeypatch.setattr(setup_cmd.subprocess, "run", fake_run)
        assert setup_cmd.run_setup() == 0
        # bootstrap_client.sh must never be shelled out to on-cluster.
        assert not any(c and c[0] == "bash" for c in calls)

    def test_launches_agent_when_present_and_confirmed(self, happy_setup, monkeypatch):
        # A detected agent + confirmed launch reaches os.execvp with the chosen
        # binary. execvp is patched so the test process is not replaced.
        monkeypatch.setattr(
            setup_cmd.shutil, "which",
            lambda name: "/usr/bin/claude" if name == "claude" else None,
        )
        execvp = MagicMock()
        monkeypatch.setattr(setup_cmd.os, "execvp", execvp)

        setup_cmd.run_setup()

        execvp.assert_called_once()
        binary, argv = execvp.call_args.args
        assert binary == "/usr/bin/claude"
        assert argv[0] == "claude" and "/berdl_start" in argv

    def test_launching_omp_from_the_wizard_sets_a_session_dir(self, happy_setup, monkeypatch):
        """A session begun from setup must be as collectable as one begun from start.

        `beril start` and `beril setup` are two launch sites for the same agent; only
        the first having a knowable transcript path is the kind of split that put the
        agent list in three places before it was shared.
        """
        monkeypatch.setattr(
            setup_cmd.shutil, "which",
            lambda name: "/usr/bin/omp" if name == "omp" else None,
        )
        monkeypatch.setattr(setup_cmd, "_prompt", lambda q, default="": "omp")
        execvp = MagicMock()
        monkeypatch.setattr(setup_cmd.os, "execvp", execvp)

        setup_cmd.run_setup()

        _binary, argv = execvp.call_args.args
        expected = str(start.omp_session_dir(happy_setup.repo))
        assert argv == ["omp", "--session-dir", expected, "/berdl_start"]
        # Under $HOME, so nothing is written into the checkout.
        assert not (happy_setup.repo / ".omp-sessions").exists()

    def test_vertex_env_injected_before_launch(self, happy_setup, monkeypatch):
        # When Vertex is enabled and claude launches, the Vertex env vars are set
        # on os.environ just before execvp.
        monkeypatch.setattr(
            setup_cmd.shutil, "which",
            lambda name: "/usr/bin/claude" if name == "claude" else None,
        )
        # Make ONLY the Vertex credentials path read as present — a blanket
        # Path.exists patch would also fool Step 2's `env_path.exists()` and
        # skip creating the .env the wizard then reads back.
        vertex_path = "/global_share/BERIL-setup/20260507_hackathon.json"
        real_exists = setup_cmd.Path.exists
        monkeypatch.setattr(
            setup_cmd.Path, "exists",
            lambda self: True if str(self) == vertex_path else real_exists(self),
        )
        monkeypatch.setattr(setup_cmd, "_confirm", lambda *a, **k: True)
        monkeypatch.setattr(setup_cmd.os, "execvp", MagicMock())

        setup_cmd.run_setup()

        assert setup_cmd.os.environ.get("CLAUDE_CODE_USE_VERTEX") == "1"
        assert setup_cmd.os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID") == "beril-hackathon-2026"
        # Vertex config was also persisted.
        assert happy_setup.saved["cfg"]["vertex"]["enabled"] is True
