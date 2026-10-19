"""Tests for knowledge/scripts/import_projects.py — the admin repo import."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import httpx
import pytest

from beril_cli import auth_store

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "knowledge" / "scripts" / "import_projects.py"
OWNER = "0000-0003-1111-2222"


def _load():
    spec = importlib.util.spec_from_file_location("import_projects_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look their module up here
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod(tmp_path, monkeypatch):
    """The script, with a stored login and a projects/ tree of its own."""
    module = _load()
    monkeypatch.setattr(auth_store, "AUTH_DIR", tmp_path / ".beril")
    monkeypatch.setattr(auth_store, "AUTH_PATH", tmp_path / ".beril" / "auth.json")
    auth_store.save(token="adm", base_url="https://srv.test", orcid_id="0009-1", display_name=None)
    repo = tmp_path / "repo"
    for name in ("alpha", "orphan", "unseen"):
        d = repo / "projects" / name
        d.mkdir(parents=True)
        (d / "README.md").write_text(f"# {name}\n")
        (d / "REPORT.md").write_text("# Report\n")
    monkeypatch.setattr(module, "REPO_ROOT", repo)
    return module


class FakeBeril:
    """Answers the admin import routes; records every request."""

    def __init__(self, monkeypatch, module, *, admin=True, batch="b1"):
        self.requests: list[httpx.Request] = []
        self.admin, self.batch = admin, batch
        real = httpx.Client
        monkeypatch.setattr(
            module.httpx, "Client",
            lambda *a, **kw: real(*a, **{**kw, "transport": httpx.MockTransport(self.serve)}),
        )

    def serve(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if not self.admin:
            return httpx.Response(403, json={"detail": "Administrator access required."})
        if request.url.path.startswith("/api/admin/context/import_status/"):
            return httpx.Response(200, json={
                "batch_id": self.batch, "project": "alpha", "status": "completed",
                "counts": {"completed": 2}, "files": [],
            })
        form = self.form(request)
        project = form.get("project")
        if project == "orphan":
            return httpx.Response(409, json={"detail": "projects/orphan is flagged: no author ORCiD"})
        if project == "unseen":
            return httpx.Response(404, json={"detail": "run the repo import first"})
        if form.get("dry_run") == "true":
            return httpx.Response(200, json={
                "results": [], "queued": 0, "failed": 0, "project": project,
                "owner_orcid": OWNER, "dry_run": True,
            })
        # No batch means every file was already current: nothing queued.
        queued, skipped = (2, 0) if self.batch else (0, 2)
        return httpx.Response(200, json={
            "results": [], "queued": queued, "failed": 0, "skipped": skipped,
            "batch_id": self.batch, "project": project, "owner_orcid": OWNER,
        })

    @staticmethod
    def form(request: httpx.Request) -> dict[str, str]:
        body = request.content
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            return dict(httpx.QueryParams(body.decode()))
        # multipart: pull the simple text fields out by name
        fields = {}
        for part in body.split(b"--")[1:]:
            if b'name="' not in part or b"filename=" in part:
                continue
            name = part.split(b'name="', 1)[1].split(b'"', 1)[0].decode()
            fields[name] = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0].decode()
        return fields


def _rows(out: str) -> dict[str, list[str]]:
    """The report's rows, keyed by project, whitespace-split."""
    return {line.split()[0]: line.split() for line in out.splitlines() if line.split()}


def test_dry_run_reports_owners_and_writes_nothing(mod, monkeypatch, capsys):
    beril = FakeBeril(monkeypatch, mod)

    assert mod.main(["--all", "--dry-run"]) == 0

    rows = _rows(capsys.readouterr().out)
    assert rows["alpha"][1:3] == ["would_import", OWNER]
    assert rows["orphan"][1] == "flagged" and rows["unseen"][1] == "not_imported"
    assert all(r.url.path == "/api/admin/context/import_files" for r in beril.requests)
    assert all(FakeBeril.form(r).get("dry_run") == "true" for r in beril.requests)


def test_import_uploads_to_the_admin_route_and_polls_its_status(mod, monkeypatch, capsys):
    beril = FakeBeril(monkeypatch, mod)

    assert mod.main(["alpha"]) == 0

    paths = [r.url.path for r in beril.requests]
    assert paths == [
        "/api/admin/context/import_files",      # dry run: who owns it
        "/api/admin/context/import_files",      # the upload
        "/api/admin/context/import_status/b1",  # poll
    ]
    upload = beril.requests[1]
    assert FakeBeril.form(upload)["project"] == "alpha"
    assert b"REPORT.md" in upload.content and b"PROJECT_METADATA.md" in upload.content
    assert upload.headers["Authorization"] == "Bearer adm"
    assert _rows(capsys.readouterr().out)["alpha"][1:3] == ["imported", OWNER]


def test_flagged_and_unimported_projects_are_reported_not_uploaded(mod, monkeypatch, capsys):
    beril = FakeBeril(monkeypatch, mod)

    assert mod.main(["orphan", "unseen"]) == 0

    assert len(beril.requests) == 2  # one dry run each, no uploads
    out = capsys.readouterr().out
    assert "1 flagged, 1 not_imported" in out


def test_force_is_sent(mod, monkeypatch):
    beril = FakeBeril(monkeypatch, mod)

    mod.main(["alpha", "--force"])

    assert FakeBeril.form(beril.requests[1]).get("force") == "true"


def test_a_project_already_current_is_reported_as_such(mod, monkeypatch, capsys):
    FakeBeril(monkeypatch, mod, batch=None)

    assert mod.main(["alpha"]) == 0
    assert _rows(capsys.readouterr().out)["alpha"][1] == "current"


def test_a_non_admin_login_stops_the_run(mod, monkeypatch, capsys):
    beril = FakeBeril(monkeypatch, mod, admin=False)

    assert mod.main(["--all"]) == 1
    assert "not a BERIL administrator" in capsys.readouterr().err
    assert len(beril.requests) == 1


def test_names_or_all_but_not_both(mod, capsys):
    assert mod.main([]) == 2
    assert mod.main(["alpha", "--all"]) == 2


def test_an_unknown_project_name_is_refused(mod, monkeypatch, capsys):
    FakeBeril(monkeypatch, mod)
    assert mod.main(["../etc"]) == 1
    assert "no project directory" in capsys.readouterr().err
