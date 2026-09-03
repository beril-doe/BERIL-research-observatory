"""Guards for the Langfuse tracing hooks.

Three failure modes matter: the hook entries silently falling out of the
settings files (nothing else would notice — tracing just stops), the
langfuse-run.sh guard regressing so unconfigured users start paying the
~0.5s SDK-import cost on every response, and the artifact hook
mis-resolving which project a session bound to.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_WRAPPER = ROOT / ".claude" / "hooks" / "langfuse-run.sh"
ARTIFACTS_HOOK = ROOT / ".claude" / "hooks" / "langfuse_artifacts.py"


def _load_artifacts_module():
    spec = importlib.util.spec_from_file_location("langfuse_artifacts", ARTIFACTS_HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_hooks_stay_wired():
    settings = ROOT / ".claude" / "settings.json"
    hooks = json.loads(settings.read_text())["hooks"]
    stop = json.dumps(hooks["Stop"])
    end = json.dumps(hooks["SessionEnd"])
    assert "langfuse-run.sh\\\" --bg langfuse_hook.py" in stop, "turn-trace hook unwired"
    assert "langfuse-run.sh\\\" langfuse_artifacts.py" in end, "artifact hook unwired"


def test_run_wrapper_guard_skips_without_config():
    # Mirrors test_statusline's interpreter-cost guard: with tracing
    # unconfigured the wrapper must exit 0 without starting Python — the
    # scripts would log/fail loudly if they ran with this stripped env.
    for env in (
        {"PATH": "/usr/bin:/bin"},
        {"PATH": "/usr/bin:/bin", "TRACE_TO_LANGFUSE": "true"},  # flag but no key
    ):
        proc = subprocess.run(
            ["bash", str(RUN_WRAPPER), "--bg", "langfuse_hook.py"],
            input="{}", capture_output=True, text=True, env=env, timeout=10,
        )
        assert proc.returncode == 0
        assert proc.stdout == "" and proc.stderr == ""


def test_artifact_hook_resolves_project_and_files(tmp_path):
    project_dir = tmp_path / "projects" / "amr_test"
    project_dir.mkdir(parents=True)
    (project_dir / "runtime.json").write_text(json.dumps({
        "sessions": [{"session_id": "sess-1", "observed_at": "2026-09-01T00:00:00Z"}],
    }))
    (project_dir / "REPORT.md").write_text("# report")
    (project_dir / "WORKLOG.md").write_text("# log")

    mod = _load_artifacts_module()
    project, files = mod.find_uploads("sess-1", tmp_path)
    assert project == "amr_test"
    assert sorted(p.name for p in files) == ["REPORT.md", "WORKLOG.md"]

    assert mod.find_uploads("unknown-session", tmp_path) is None


def test_artifact_hook_fails_open_without_config(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ARTIFACTS_HOOK)],
        input='{"session_id": "sess-1"}',
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        timeout=30,
    )
    assert proc.returncode == 0
    assert proc.stdout == ""
