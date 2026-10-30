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
