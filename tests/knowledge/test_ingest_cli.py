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

import io
import json
import zipfile

from observatory_context import beril_submit


ARCHIVED_YAML = (
    "project_id: alpha\nstatus: complete\napproval:\n  by: \"0009-1\"\n"
    "  at: \"2026-11-01T00:00:00Z\"\n  report_hash: \"sha256:" + "ab" * 32 + "\"\n"
)


@pytest.fixture
def record_env(tmp_path, monkeypatch):
    """The script module with a login, a project archived from a snapshot
    (its record kept under the state dir, as the upload tool keeps it), and a
    fake BERIL answering the submissions routes. Built without ``mirror``:
    both would patch the one global ``httpx.Client``."""
    monkeypatch.setattr(auth_store, "AUTH_DIR", tmp_path / ".beril")
    monkeypatch.setattr(auth_store, "AUTH_PATH", tmp_path / ".beril" / "auth.json")
    auth_store.save(token="beril_abc", base_url="https://srv.test", orcid_id="0009-1",
                    display_name=None)
    module = _load_script()
    snapshot = tmp_path / "snapshot"
    (snapshot / "figures").mkdir(parents=True)
    (snapshot / "REPORT.md").write_text("# R\n\n![f](figures/f.png)\n")
    (snapshot / "README.md").write_text("# A\n")
    (snapshot / "figures" / "f.png").write_bytes(b"\x89PNG" + bytes(8))
    (snapshot / "data.csv").write_text("a,b\n")
    (snapshot / "project_metadata.json").write_text("{}")
    (snapshot / "beril.yaml").write_text(ARCHIVED_YAML)
    files = beril_submit.file_entries(snapshot, sorted(p for p in snapshot.rglob("*") if p.is_file()))
    repo = tmp_path / "repo"
    real_from_env = module.ContextConfig.from_env
    monkeypatch.setattr(
        module.ContextConfig, "from_env",
        classmethod(lambda cls, repo_root=None: real_from_env(repo_root=repo)),
    )
    state_dir = real_from_env(repo_root=repo).state_dir
    beril_submit.save_pending(
        state_dir, "alpha", snapshot, files=files, archive_path="s3a://b/t/projects/alpha/",
        submitted_at="2026-11-02T00:00:00+00:00",
    )
    requests: list[httpx.Request] = []
    state = {"missing": ["figures/f.png"], "refuse": False}

    def serve(request):
        requests.append(request)
        if state["refuse"]:
            return httpx.Response(503, json={"detail": "down"})
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
    return module, requests, state_dir, files, state


def _verdict(capsys):
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def _posted(request):
    """(manifest, {bundle path: bytes}) from a record post."""
    body = request.read()
    boundary = request.headers["Content-Type"].split("boundary=", 1)[1].encode()
    manifest, bundle = None, None
    for part in body.split(b"--" + boundary):
        head, _, data = part.partition(b"\r\n\r\n")
        data = data.rstrip(b"\r\n").removesuffix(b"--")
        if b'name="manifest.json"' in head:
            manifest = json.loads(data)
        elif b'name="bundle.zip"' in head:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                bundle = {n: zf.read(n) for n in zf.namelist()}
    return manifest, bundle


def test_record_posts_the_kept_record_then_the_missing_figure_and_drops_it(record_env, capsys):
    module, requests, state_dir, _, _ = record_env

    assert module.run_record("alpha") == 0

    verdict = _verdict(capsys)
    assert verdict["status"] == "ok" and verdict["id"] == "sub-9" and verdict["missing"] == []
    assert [r.method for r in requests] == ["POST", "PUT"]
    assert requests[0].url.path == "/api/context/submissions"
    assert requests[0].headers["Authorization"] == "Bearer beril_abc"
    assert requests[1].url.path == "/api/context/submissions/sub-9/files/figures/f.png"
    assert beril_submit.load_pending(state_dir, "alpha") is None


def test_record_sends_the_archive_not_the_checkout_as_submit_left_it(record_env, tmp_path, capsys):
    # After archiving, /submit's Phase 3c rewrites beril.yaml and writes
    # SUBMITTED.md, and the generated project_metadata.json is gone. The retry
    # must still describe the archive exactly.
    module, requests, _, files, _ = record_env
    checkout = tmp_path / "repo" / "projects" / "alpha"
    checkout.mkdir(parents=True)
    (checkout / "beril.yaml").write_text(ARCHIVED_YAML + "submissions:\n  - status: success\n")
    (checkout / "SUBMITTED.md").write_text("# Submitted\n")
    (checkout / "REPORT.md").write_text("# R\n\n![f](figures/f.png)\n")

    module.run_record("alpha")

    manifest, bundle = _posted(requests[0])
    assert manifest["files"] == files
    assert "project_metadata.json" in {f["path"] for f in manifest["files"]}
    assert "SUBMITTED.md" not in {f["path"] for f in manifest["files"]}
    assert bundle["beril.yaml"] == ARCHIVED_YAML.encode()
    assert manifest["archive_path"] == "s3a://b/t/projects/alpha/"
    assert manifest["submitted_at"] == "2026-11-02T00:00:00+00:00"
    assert manifest["owner_orcid"] == "0009-1"
    assert requests[1].read() == b"\x89PNG" + bytes(8)


def test_record_without_a_kept_record_fails_and_says_to_re_submit(record_env, capsys):
    module, requests, state_dir, _, _ = record_env
    beril_submit.drop_pending(state_dir, "alpha")

    module.run_record("alpha")

    verdict = _verdict(capsys)
    assert verdict["status"] == "failed" and "re-run /submit" in verdict["reason"]
    assert requests == []


def test_a_failed_retry_keeps_the_record_for_the_next(record_env, capsys):
    module, requests, state_dir, _, state = record_env
    state["refuse"] = True

    module.run_record("alpha")

    assert _verdict(capsys)["status"] == "failed"
    assert beril_submit.load_pending(state_dir, "alpha") is not None


def test_a_kept_record_of_an_unapproved_project_is_skipped_and_dropped(record_env, capsys):
    module, requests, state_dir, _, _ = record_env
    kept = beril_submit.load_pending(state_dir, "alpha")
    (kept.root / "beril.yaml").write_text("project_id: alpha\n")

    module.run_record("alpha")

    verdict = _verdict(capsys)
    assert verdict["status"] == "skipped" and "approval" in verdict["reason"]
    assert requests == [] and beril_submit.load_pending(state_dir, "alpha") is None


def test_record_without_a_login_is_skipped(record_env, capsys):
    module, requests, _, _, _ = record_env
    auth_store.AUTH_PATH.unlink()
    module.run_record("alpha")
    assert _verdict(capsys)["status"] == "skipped" and requests == []


def test_record_for_an_unknown_project_is_failed_not_a_crash(record_env, capsys):
    module, requests, _, _, _ = record_env
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
