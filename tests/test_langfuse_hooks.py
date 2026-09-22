"""Guards for the Langfuse tracing hooks.

Three failure modes matter: the hook entries silently falling out of the
settings files (nothing else would notice — tracing just stops), the
langfuse-run.sh guard regressing so unconfigured users start paying the
~0.5s SDK-import cost on every response, the hooks reaching Langfuse any way
other than through the BERIL relay (which would need keys on the laptop),
and the artifact hook mis-resolving which project a session bound to.
"""

from __future__ import annotations

import importlib.util
import io
import json
import runpy
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

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
    # --bg on SessionEnd too: its hooks share a 1.5s budget, which the SDK
    # import alone nearly consumes; foreground would be cancelled mid-upload.
    assert "langfuse-run.sh\\\" --bg langfuse_artifacts.py" in end, "artifact hook unwired"


def test_run_wrapper_guard_skips_without_config(tmp_path):
    # Mirrors test_statusline's interpreter-cost guard: with tracing
    # unconfigured the wrapper must exit 0 without starting Python — the
    # scripts would log/fail loudly if they ran with this stripped env.
    for env in (
        {"PATH": "/usr/bin:/bin"},
        {"PATH": "/usr/bin:/bin", "TRACE_TO_LANGFUSE": "true"},  # flag, no HOME
        {"PATH": "/usr/bin:/bin", "TRACE_TO_LANGFUSE": "true", "HOME": str(tmp_path)},  # not logged in
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


def test_hooks_reach_langfuse_only_through_the_relay(tmp_path, monkeypatch):
    # Credential = the `beril login` record; host = BERIL's /lf relay; the
    # PAT rides as the Basic password. Nothing here is a Langfuse key.
    auth = tmp_path / "auth.json"
    auth.write_text(json.dumps({
        "token": "beril_abc", "base_url": "https://beril.test/",
        "orcid_id": "0000-0001-2345-6789", "display_name": "Alice",
        "ov_user_key": "fake-ov-credential",
    }))
    monkeypatch.setattr("beril_cli.auth_store.AUTH_PATH", auth)
    monkeypatch.delenv("LANGFUSE_USER_ID", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "fake-provider-credential")

    mod = _load_artifacts_module()
    kwargs = mod.relay_client_kwargs()
    assert kwargs["base_url"] == "https://beril.test/lf"
    assert kwargs["secret_key"] == "beril_abc"
    assert kwargs["public_key"] == "beril"
    assert kwargs["mask"](data={"values": ["beril_abc", "fake-ov-credential", "fake-provider-credential"]}) == {
        "values": ["[REDACTED]"] * 3,
    }
    assert mod.get_user_id() == "0000-0001-2345-6789"

    # A stale LANGFUSE_BASE_URL from the pre-relay setup must not win: the SDK
    # resolves base_url > env > host, and the PAT must never leave for Langfuse
    # Cloud directly. Real SDK, tracing off so nothing is sent.
    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://other-langfuse.test")
    from langfuse import Langfuse
    lf = Langfuse(**kwargs, tracing_enabled=False)
    assert lf._resources.base_url == "https://beril.test/lf"

    monkeypatch.setattr("beril_cli.auth_store.AUTH_PATH", tmp_path / "missing.json")
    mod = _load_artifacts_module()
    assert mod.relay_client_kwargs() is None
    assert mod.get_user_id() is None


def test_mask_covers_the_cborg_credential_the_setup_guide_sets(tmp_path, monkeypatch):
    # docs/getting_started.md Option B: ANTHROPIC_AUTH_TOKEN=$CBORG_API_KEY.
    # A traced session that runs `env` must not ship either value (#438).
    auth = tmp_path / "auth.json"
    auth.write_text(json.dumps({
        "token": "beril_abc", "base_url": "https://beril.test/",
        "orcid_id": "0000-0001-2345-6789", "display_name": "Alice",
    }))
    monkeypatch.setattr("beril_cli.auth_store.AUTH_PATH", auth)
    monkeypatch.setenv("CBORG_API_KEY", "fake-cborg-credential")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "fake-cborg-credential")

    mask = _load_artifacts_module().relay_client_kwargs()["mask"]
    env_dump = (
        "ANTHROPIC_AUTH_TOKEN=fake-cborg-credential\n"
        "CBORG_API_KEY=fake-cborg-credential\n"
        "ANTHROPIC_BASE_URL=https://api.cborg.lbl.gov"
    )
    assert mask(data=env_dump) == (
        "ANTHROPIC_AUTH_TOKEN=[REDACTED]\n"
        "CBORG_API_KEY=[REDACTED]\n"
        "ANTHROPIC_BASE_URL=https://api.cborg.lbl.gov"
    )


def test_turn_text_is_complete_unless_a_limit_is_requested(monkeypatch):
    monkeypatch.delenv("CC_LANGFUSE_MAX_CHARS", raising=False)
    monkeypatch.syspath_prepend(str(ARTIFACTS_HOOK.parent))
    hook = runpy.run_path(str(ARTIFACTS_HOOK.with_name("langfuse_hook.py")))
    text = "password=FAKE_CANARY\n" + "long tool output " * 2000 + "END"
    actual, metadata = hook["truncate_text"](text)
    assert actual == text
    assert metadata == {"truncated": False, "orig_len": len(text)}
    limited, metadata = hook["truncate_text"](text, max_chars=100)
    assert limited == text[:100]
    assert metadata["truncated"] is True


def test_mask_only_known_credentials_and_authorization_headers():
    mod = _load_artifacts_module()
    scientific = {
        "token": "gene-token", "secret": "secreted protein", "password": "study label",
        "api_key": "column name", "token_count": 3,
        "content": "password=study-label; token=gene-token\n" + "résultats " * 4000 + "END",
    }
    assert mod.redact(scientific) == scientific
    assert mod.redact(data="unlabelled known-credential", secrets=("known-credential",)) == "unlabelled [REDACTED]"
    assert mod.redact({"headers": {"Authorization": "Bearer fake-bearer", "X-Study": "keep"}}) == {
        "headers": {"Authorization": "Bearer [REDACTED]", "X-Study": "keep"},
    }
    assert mod.redact([{"proxy-authorization": "Basic ZmFrZTp0ZXN0"}, None, 3]) == [
        {"proxy-authorization": "Basic [REDACTED]"}, None, 3,
    ]
    assert mod.redact({"AUTHORIZATION": "opaque-credential"}) == {"AUTHORIZATION": "[REDACTED]"}
    for original, expected in (
        ('{"Authorization": "Bearer fake-bearer", "token_count": 3}',
         '{"Authorization": "Bearer [REDACTED]", "token_count": 3}'),
        ("curl -H 'Authorization: Basic ZmFrZTp0ZXN0' https://example.test",
         "curl -H 'Authorization: Basic [REDACTED]' https://example.test"),
        ("Proxy-Authorization: Token fake-token\r\nResearch follows.",
         "Proxy-Authorization: Token [REDACTED]\r\nResearch follows."),
    ):
        assert mod.redact(original) == expected
        assert mod.redact(expected) == expected


def test_sdk_export_failures_reach_the_hook_log(tmp_path, monkeypatch):
    # Delivery is at-most-once, so the log is the only evidence of a dropped
    # export; the exporter logs failures instead of raising.
    import logging

    mod = _load_artifacts_module()
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "artifacts.log")
    mod.route_sdk_logs()
    logging.getLogger("opentelemetry.exporter.otlp.proto.http.trace_exporter").error(
        "Failed to export span batch code: 401"
    )
    assert "401" in (tmp_path / "artifacts.log").read_text()


def test_artifact_hook_masks_credentials_preserving_other_bytes(tmp_path, monkeypatch):
    import langfuse
    import langfuse.media

    mod = _load_artifacts_module()
    project = tmp_path / "projects" / "fidelity_test"
    project.mkdir(parents=True)
    (project / "runtime.json").write_text(json.dumps({
        "sessions": [{"session_id": "fidelity-session", "observed_at": "2026-09-22T00:00:00Z"}],
    }))
    original = ("# Résultats\r\npassword=study-label\r\nAuthorization: Bearer fake-bearer\r\n"
                "known-credential\r\n" + "Ordinary science text.\r\n" * 2000 + "END").encode("utf-8") + b"\xff"
    expected = original.replace(b"fake-bearer", b"[REDACTED]").replace(b"known-credential", b"[REDACTED]")
    for name in mod.ARTIFACTS:
        (project / name).write_bytes(original)
    monkeypatch.setenv("TRACE_TO_LANGFUSE", "true")
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "artifacts.log")
    monkeypatch.setattr(mod, "relay_client_kwargs", lambda: {
        "public_key": "beril", "mask": lambda data: mod.redact(data, secrets=("known-credential",)),
    })
    monkeypatch.setattr(mod, "get_user_id", lambda: "test-user")
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"session_id": "fidelity-session"}'))
    client = MagicMock()
    monkeypatch.setattr(langfuse, "Langfuse", lambda **kwargs: client)
    media = MagicMock(wraps=langfuse.media.LangfuseMedia)
    monkeypatch.setattr(langfuse.media, "LangfuseMedia", media)

    assert mod.main() == 0
    assert media.call_count == 3
    for call in media.call_args_list:
        assert call.kwargs["content_bytes"] == expected
        assert call.kwargs["content_type"] == "text/markdown"
    client.start_observation.assert_called_once()
    client.shutdown.assert_called_once()
    for name in mod.ARTIFACTS:
        assert (project / name).read_bytes() == original


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
