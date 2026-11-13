from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "knowledge" / "scripts" / "ingest_context.py"


def test_empty_project_is_rejected_not_silent_success():
    """`--project ""` must be rejected, not reported as a successful no-op.

    The validator runs before any server contact, so this needs no server.
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", ""],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "Ingest finished" not in combined
    assert "Project ID must be a simple directory name" in proc.stderr
    assert "Traceback" not in proc.stderr


def _load_script():
    import importlib.util

    spec = importlib.util.spec_from_file_location("ingest_context_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mirror_withdraws_approval_gated_memories_the_project_lacks(tmp_path):
    """`/submit` deletes these memories when the approved REPORT drops the
    section; the mirror follows with an explicit withdrawal for each one that
    is absent. One the project still carries is never withdrawn."""
    script = _load_script()
    staged = tmp_path / "staged"
    (staged / "memories").mkdir(parents=True)
    (staged / "memories" / "performance.md").write_text("fast", encoding="utf-8")
    (staged / "memories" / "pitfalls.md").write_text("careful", encoding="utf-8")

    assert script._withdrawn_memories(staged) == ["memories/discoveries.md"]


def test_mirror_withdraws_both_gated_memories_when_none_are_staged(tmp_path):
    script = _load_script()
    staged = tmp_path / "staged"
    staged.mkdir()

    assert script._withdrawn_memories(staged) == [
        "memories/discoveries.md", "memories/performance.md"
    ]


def test_remove_requires_json_mode():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", "x", "--remove", "a.md"],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert proc.returncode != 0
    assert "--remove can only be used with --json" in proc.stderr


# --- the mirror's preflight ---------------------------------------------------


import httpx  # noqa: E402
import pytest  # noqa: E402

from beril_cli import auth_store, context_client  # noqa: E402


@pytest.fixture
def mirror(tmp_path, monkeypatch):
    """The script module, a stored login, and a fake BERIL answering health."""
    monkeypatch.setattr(auth_store, "AUTH_DIR", tmp_path / ".beril")
    monkeypatch.setattr(auth_store, "AUTH_PATH", tmp_path / ".beril" / "auth.json")
    auth_store.save(token="beril_abc", base_url="https://srv.test", orcid_id="0009-1",
                    display_name=None)
    calls: list[httpx.Request] = []
    answer = {"response": httpx.Response(200, json={"status": "ok"})}

    def serve(request):
        calls.append(request)
        reply = answer["response"]
        if isinstance(reply, Exception):
            raise reply
        return reply

    real_client = httpx.Client
    monkeypatch.setattr(
        context_client.httpx, "Client",
        lambda *a, **kw: real_client(*a, **{**kw, "transport": httpx.MockTransport(serve)}),
    )
    module = _load_script()
    return module, answer, calls


def test_preflight_checks_context_health_through_beril(mirror):
    """The mirror never touches the store's own routes: the user-facing
    `/api/ov/*` surface is going admin-only, so the gate is BERIL's own
    authenticated `/api/context/health`."""
    module, _answer, calls = mirror

    record, reason = module._preflight()

    assert record is not None and reason == "context service available"
    assert [c.url.path for c in calls] == ["/api/context/health"]
    assert calls[0].headers["Authorization"] == "Bearer beril_abc"


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        (httpx.Response(200, json={"status": "unavailable"}), "context service is unavailable"),
        (httpx.Response(401, json={"detail": "no"}), "health check failed"),
        (httpx.ConnectError("refused"), "health check failed"),
    ],
)
def test_preflight_skips_when_the_context_layer_cannot_take_an_upload(mirror, reply, expected):
    module, answer, _calls = mirror
    answer["response"] = reply

    record, reason = module._preflight()

    assert record is None
    assert expected in reason


def test_preflight_without_a_login(mirror):
    module, _answer, calls = mirror
    auth_store.clear()

    record, reason = module._preflight()

    assert record is None and "beril login" in reason
    assert calls == []


# --- --record: re-send the submission record --------------------------------

import hashlib
import json

from observatory_context import beril_submit


@pytest.fixture
def record_env(tmp_path, monkeypatch):
    """The script module with a login, a project under the repo root, and a
    fake BERIL answering the submissions routes. Built without ``mirror``:
    both would patch the one global ``httpx.Client``."""
    monkeypatch.setattr(auth_store, "AUTH_DIR", tmp_path / ".beril")
    monkeypatch.setattr(auth_store, "AUTH_PATH", tmp_path / ".beril" / "auth.json")
    auth_store.save(token="beril_abc", base_url="https://srv.test", orcid_id="0009-1",
                    display_name=None)
    module = _load_script()
    root = tmp_path / "repo" / "projects" / "alpha"
    (root / "figures").mkdir(parents=True)
    (root / "REPORT.md").write_text("# R\n\n![f](figures/f.png)\n")
    (root / "README.md").write_text("# A\n")
    (root / "figures" / "f.png").write_bytes(b"\x89PNG" + bytes(8))
    (root / "project_metadata.json").write_text("{}")
    (root / "beril.yaml").write_text(
        "project_id: alpha\napproval:\n  by: \"0009-1\"\n  at: \"2026-11-01T00:00:00Z\"\n"
        "  report_hash: \"sha256:" + "ab" * 32 + "\"\nsubmissions:\n"
        "  - status: failed\n    archive_key: \"s3a://old/\"\n"
        "  - status: success\n    archive_key: \"s3a://b/t/projects/alpha/\"\n"
    )
    real_from_env = module.ContextConfig.from_env
    monkeypatch.setattr(
        module.ContextConfig, "from_env",
        classmethod(lambda cls, repo_root=None: real_from_env(repo_root=tmp_path / "repo")),
    )
    requests: list[httpx.Request] = []
    state = {"missing": ["figures/f.png"]}

    def serve(request):
        requests.append(request)
        if request.method == "POST":
            status = "complete" if not state["missing"] else "pending"
            return httpx.Response(200, json={"id": "sub-9", "status": status,
                                             "missing": state["missing"]})
        state["missing"] = []
        return httpx.Response(200, json={"status": "complete", "missing": []})

    real_client = httpx.Client
    monkeypatch.setattr(
        beril_submit.httpx, "Client",
        lambda *a, **kw: real_client(*a, **{**kw, "transport": httpx.MockTransport(serve)}),
    )
    return module, requests


def _verdict(capsys):
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_record_posts_manifest_then_the_missing_figure(record_env, capsys):
    module, requests = record_env

    assert module.run_record("alpha") == 0

    verdict = _verdict(capsys)
    assert verdict["status"] == "ok" and verdict["id"] == "sub-9" and verdict["missing"] == []
    assert [r.method for r in requests] == ["POST", "PUT"]
    assert requests[0].url.path == "/api/context/submissions"
    assert requests[0].headers["Authorization"] == "Bearer beril_abc"
    assert requests[1].url.path == "/api/context/submissions/sub-9/files/figures/f.png"


def test_record_defaults_the_archive_to_the_last_successful_submission(record_env, capsys):
    module, requests = record_env
    module.run_record("alpha")
    body = requests[0].read()
    assert b"s3a://b/t/projects/alpha/" in body and b"s3a://old/" not in body
    assert b'"owner_orcid": "0009-1"' in body
    # The archive's generated metadata file is skipped, as the archive walker skips it.
    assert b"project_metadata.json" not in body


def test_record_without_an_archive_fails_and_asks_for_the_path(record_env, tmp_path, capsys):
    module, requests = record_env
    yaml_path = tmp_path / "repo" / "projects" / "alpha" / "beril.yaml"
    yaml_path.write_text(yaml_path.read_text().split("submissions:")[0])

    module.run_record("alpha")
    verdict = _verdict(capsys)
    assert verdict["status"] == "failed" and "--archive-path" in verdict["reason"]
    assert requests == []

    module.run_record("alpha", "s3a://given/")
    assert _verdict(capsys)["status"] == "ok" and b"s3a://given/" in requests[0].read()


def test_record_without_a_login_is_skipped(record_env, capsys):
    module, requests = record_env
    auth_store.AUTH_PATH.unlink()
    module.run_record("alpha")
    assert _verdict(capsys)["status"] == "skipped" and requests == []


def test_record_for_an_unknown_project_is_failed_not_a_crash(record_env, capsys):
    module, requests = record_env
    module.run_record("nope")
    verdict = _verdict(capsys)
    assert verdict["status"] == "failed" and "nope" in verdict["reason"] and requests == []


def test_record_flags_need_project_and_exclude_json():
    module = _load_script()
    parser = module.build_parser()
    args = parser.parse_args(["--record", "--project", "alpha"])
    assert args.record and args.project == "alpha"
    with pytest.raises(SystemExit):
        parser.parse_args(["--record", "--all", "--project", "alpha"])
