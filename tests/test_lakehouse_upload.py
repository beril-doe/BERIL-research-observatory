"""Tests for tools/lakehouse_upload.py.

The upload tool shells out to `mc` for every remote operation, so these tests
stub `_mc` rather than the network: each test declares the exact mc call
sequence it expects and asserts on the recorded calls. That keeps the
integrity-boundary behaviours — SKIP_PATTERNS filtering, the pre-upload clear,
the manifest+1 count check, the metadata cleanup — testable without a MinIO.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


TOOL = Path(__file__).parents[1] / "tools" / "lakehouse_upload.py"


@pytest.fixture()
def lu(monkeypatch):
    """Load lakehouse_upload as a fresh module per test.

    Fresh per test because `main()` reassigns the TENANT_PATH / LAKEHOUSE_BASE /
    S3A_BASE globals under --tenant-path; a shared module would leak that
    retarget into every later test.
    """
    spec = importlib.util.spec_from_file_location("lakehouse_upload", TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["lakehouse_upload"] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop("lakehouse_upload", None)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A minimal observatory repo with one project."""
    project = tmp_path / "projects" / "demo"
    project.mkdir(parents=True)
    (project / "README.md").write_text(
        "# Demo Project\n"
        "\n"
        "## Status\n"
        "complete\n"
        "\n"
        "## Authors\n"
        "Ada Lovelace\n"
        "Alan Turing\n"
        "\n"
        "## Notes\n"
        "not an author\n"
    )
    (project / "REPORT.md").write_text("# Report\n")
    data = project / "data"
    data.mkdir()
    (data / "results.csv").write_text("a,b\n1,2\n")
    return tmp_path


# --- clean_tenant_path -----------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("tenant-general-warehouse/nmdc", "tenant-general-warehouse/nmdc"),
        ("  tenant-general-warehouse/nmdc  ", "tenant-general-warehouse/nmdc"),
        ("/tenant-general-warehouse/nmdc/", "tenant-general-warehouse/nmdc"),
        ("tenant-general-warehouse//nmdc", "tenant-general-warehouse/nmdc"),
        ("nmdc", "nmdc"),
    ],
)
def test_clean_tenant_path_normalizes(lu, raw, expected):
    assert lu.clean_tenant_path(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "s3a://cdm-lake/tenant/nmdc",          # URI scheme
        "tenant general/nmdc",                  # whitespace
        "tenant/../../etc",                     # traversal
        "",                                     # empty
        "   ",                                  # empty after strip
        "/",                                    # no segments
        "tenant-general-warehouse/projects",    # trailing 'projects'
    ],
)
def test_clean_tenant_path_rejects_bad_input(lu, raw):
    """Every rejection path must exit rather than return a usable path.

    A silently-accepted `..` or trailing `projects` would archive into the wrong
    prefix — and the pre-upload clear (`mc rm --recursive`) runs against whatever
    prefix comes out of here, so a bad value is destructive, not just wrong.
    """
    with pytest.raises(SystemExit):
        lu.clean_tenant_path(raw)


# --- _extract_readme_metadata ---------------------------------------------


def test_extract_readme_metadata_reads_sections(lu, repo):
    meta = lu._extract_readme_metadata(repo / "projects" / "demo")
    assert meta["title"] == "Demo Project"
    assert meta["status"] == "complete"
    assert meta["authors"] == "Ada Lovelace\nAlan Turing"


def test_extract_readme_metadata_stops_at_next_section(lu, repo):
    """`## Notes` must close the authors section, not append to it."""
    meta = lu._extract_readme_metadata(repo / "projects" / "demo")
    assert "not an author" not in meta["authors"]


def test_extract_readme_metadata_missing_readme(lu, tmp_path):
    empty = tmp_path / "no_readme"
    empty.mkdir()
    assert lu._extract_readme_metadata(empty) == {
        "title": "",
        "status": "",
        "authors": "",
    }


# --- get_upload_manifest ---------------------------------------------------


def test_manifest_lists_files_with_relative_paths(lu, repo):
    manifest = lu.get_upload_manifest(repo / "projects" / "demo")
    rels = {f["relative_path"] for f in manifest}
    assert rels == {"README.md", "REPORT.md", str(Path("data/results.csv"))}


def test_manifest_records_size_and_extension(lu, repo):
    manifest = lu.get_upload_manifest(repo / "projects" / "demo")
    csv = next(f for f in manifest if f["relative_path"].endswith("results.csv"))
    assert csv["extension"] == ".csv"
    assert csv["size_bytes"] == len("a,b\n1,2\n")
    assert csv["modified_date"].tzinfo is not None


def test_manifest_skips_transient_files(lu, repo):
    """SKIP_PATTERNS is the integrity boundary — nothing in it may be archived.

    `.submit.lock` is held by /submit through Phase 3, so it is genuinely
    present on disk during a real upload; `project_metadata.json` is added back
    explicitly by upload_project and must not be double-counted from the walk.
    """
    project = repo / "projects" / "demo"
    (project / ".submit.lock").write_text("held")
    (project / "project_metadata.json").write_text("{}")
    (project / ".DS_Store").write_text("junk")
    (project / "__pycache__").mkdir()
    (project / "__pycache__" / "mod.pyc").write_text("bytes")
    (project / ".ipynb_checkpoints").mkdir()
    (project / ".ipynb_checkpoints" / "nb.ipynb").write_text("{}")

    rels = {f["relative_path"] for f in lu.get_upload_manifest(project)}
    assert rels == {"README.md", "REPORT.md", str(Path("data/results.csv"))}


# --- generate_metadata -----------------------------------------------------


@pytest.fixture()
def stub_git(lu, monkeypatch):
    monkeypatch.setattr(lu, "_get_git_info", lambda base: ("beril-test", "abc123"))


def test_generate_metadata_shape(lu, repo, stub_git, monkeypatch):
    monkeypatch.setenv("USER", "ada")
    meta = lu.generate_metadata("demo", repo)

    assert meta["project_id"] == "demo"
    assert meta["title"] == "Demo Project"
    assert meta["status"] == "complete"
    assert meta["uploaded_by"] == "ada"
    assert meta["git_branch"] == "beril-test"
    assert meta["git_commit"] == "abc123"
    assert meta["lakehouse_path"] == f"{lu.S3A_BASE}/demo/"
    assert meta["local_path"] == "projects/demo/"
    assert meta["total_files"] == 3
    assert meta["total_size_bytes"] == sum(
        f["size_bytes"] for f in lu.get_upload_manifest(repo / "projects" / "demo")
    )


def test_generate_metadata_splits_out_data_files(lu, repo, stub_git):
    meta = lu.generate_metadata("demo", repo)
    assert [f["path"] for f in meta["data_files"]] == [str(Path("data/results.csv"))]
    assert meta["data_files"][0]["name"] == "results.csv"
    assert meta["data_files"][0]["extension"] == ".csv"
    assert {f["path"] for f in meta["files"]} == {
        "README.md", "REPORT.md", str(Path("data/results.csv"))
    }


def test_generate_metadata_is_json_serializable(lu, repo, stub_git):
    """upload_project writes this with `default=str` — datetimes must survive."""
    meta = lu.generate_metadata("demo", repo)
    assert json.loads(json.dumps(meta, default=str))["project_id"] == "demo"


def test_generate_metadata_excludes_stale_metadata_file(lu, repo, stub_git):
    """A leftover project_metadata.json must not self-list into the new files[].

    If it did, `expected_remote_count = len(manifest) + 1` would expect two
    copies of the same relative path and a clean retry would report a false
    partial upload.
    """
    (repo / "projects" / "demo" / "project_metadata.json").write_text('{"stale": 1}')
    meta = lu.generate_metadata("demo", repo)
    assert meta["total_files"] == 3
    assert "project_metadata.json" not in {f["path"] for f in meta["files"]}


# --- submit_to_context_service --------------------------------------------


@pytest.fixture()
def mirror_repo(repo: Path) -> Path:
    """`repo` plus a knowledge/scripts/ingest_context.py so the mirror is found."""
    scripts = repo / "knowledge" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "ingest_context.py").write_text("# stub\n")
    return repo


def _stub_run(lu, monkeypatch, *, stdout="", stderr="", returncode=0, record=None):
    class Proc:
        pass

    def fake_run(cmd, **kwargs):
        if record is not None:
            record.append((cmd, kwargs))
        proc = Proc()
        proc.stdout, proc.stderr, proc.returncode = stdout, stderr, returncode
        return proc

    monkeypatch.setattr(lu.subprocess, "run", fake_run)


def test_mirror_script_path_prefers_base_path(lu, mirror_repo):
    assert lu._mirror_script_path(mirror_repo) == (
        mirror_repo / "knowledge" / "scripts" / "ingest_context.py"
    )


def test_mirror_skips_when_script_missing(lu, repo, monkeypatch):
    """No knowledge/scripts/ingest_context.py anywhere → clean skip, no raise.

    `_mirror_script_path` falls back to this tool's own repo root, which really
    does hold the script, so a tmp_path base alone would not reach this branch
    (and would spawn a real `uv`). Stub the lookup to force the miss.
    """
    monkeypatch.setattr(lu, "_mirror_script_path", lambda base: None)
    outcome = lu.submit_to_context_service("demo", repo)
    assert outcome["status"] == "skipped"
    assert "not found" in outcome["reason"]


def test_mirror_parses_verdict(lu, mirror_repo, monkeypatch):
    _stub_run(lu, monkeypatch, stdout='{"status": "ok", "reason": "ingested 3 docs"}\n')
    assert lu.submit_to_context_service("demo", mirror_repo) == {
        "status": "ok",
        "reason": "ingested 3 docs",
    }


def test_mirror_reads_last_line_of_stdout(lu, mirror_repo, monkeypatch):
    """uv prints build/resolve chatter before the verdict; only the last line counts."""
    _stub_run(
        lu,
        monkeypatch,
        stdout='Resolved 12 packages\nInstalled openviking\n{"status": "skipped", "reason": "not logged in"}\n\n',
    )
    assert lu.submit_to_context_service("demo", mirror_repo) == {
        "status": "skipped",
        "reason": "not logged in",
    }


def test_mirror_invokes_uv_run_script_with_json(lu, mirror_repo, monkeypatch):
    calls = []
    _stub_run(lu, monkeypatch, stdout='{"status": "ok"}', record=calls)
    lu.submit_to_context_service("demo", mirror_repo)

    cmd, kwargs = calls[0]
    assert cmd[:3] == ["uv", "run", "--script"]
    assert cmd[3].endswith(str(Path("knowledge/scripts/ingest_context.py")))
    assert cmd[4:] == ["--project", "demo", "--json"]
    assert kwargs["cwd"] == str(mirror_repo.resolve())


def test_mirror_skips_when_uv_missing(lu, mirror_repo, monkeypatch):
    def boom(*a, **kw):
        raise FileNotFoundError("uv")

    monkeypatch.setattr(lu.subprocess, "run", boom)
    outcome = lu.submit_to_context_service("demo", mirror_repo)
    assert outcome["status"] == "skipped"
    assert "uv" in outcome["reason"]


@pytest.mark.parametrize(
    "stdout",
    ["", "not json at all", '{"no_status": true}', "[1, 2, 3]"],
)
def test_mirror_degrades_to_skip_on_bad_output(lu, mirror_repo, monkeypatch, stdout):
    """A crashed or non-conforming mirror script must never fail the upload."""
    _stub_run(lu, monkeypatch, stdout=stdout, stderr="Traceback\nImportError: openviking", returncode=1)
    outcome = lu.submit_to_context_service("demo", mirror_repo)
    assert outcome["status"] == "skipped"
    assert "ImportError: openviking" in outcome["reason"]


# --- upload_project --------------------------------------------------------


class FakeMC:
    """Records mc invocations and replays scripted responses.

    `remote` models the objects at the destination prefix: `cp` adds to it,
    `rm --recursive` clears it, `ls --recursive` renders it one-object-per-line
    the way real `mc ls` output is counted by the tool.
    """

    def __init__(self, *, alias_ok=True, cp_failures=(), rm_rc=0, prepopulated=()):
        self.calls = []
        self.alias_ok = alias_ok
        self.cp_failures = set(cp_failures)
        self.rm_rc = rm_rc
        self.remote = list(prepopulated)

    def __call__(self, *args, capture=True):
        self.calls.append(list(args))
        verb = args[0]

        if verb == "alias":
            return (0 if self.alias_ok else 1), "", ""

        if verb == "ls":
            if not self.remote:
                return 1, "", "object not found"
            return 0, "\n".join(f"[date] 1KiB {name}" for name in self.remote), ""

        if verb == "rm":
            if self.rm_rc == 0:
                self.remote = []
            return self.rm_rc, "", ("rm denied" if self.rm_rc else "")

        if verb == "cp":
            target = args[2]
            rel = target.split("/projects/demo/", 1)[-1]
            if rel in self.cp_failures:
                return 1, "", "cp failed"
            self.remote.append(rel)
            return 0, "", ""

        raise AssertionError(f"unexpected mc verb: {verb}")

    def verbs(self):
        return [c[0] for c in self.calls]

    def cp_targets(self):
        return [c[2].split("/projects/demo/", 1)[-1] for c in self.calls if c[0] == "cp"]


class LosesAFile(FakeMC):
    """`mc cp` reports success but the object never lands at the prefix.

    This is the shape of a silent partial upload — the case the manifest+1
    count check exists to catch.
    """

    def __call__(self, *args, capture=True):
        rc, out, err = super().__call__(*args, capture=capture)
        if args[0] == "cp" and args[2].endswith("REPORT.md"):
            self.remote.remove("REPORT.md")
        return rc, out, err


@pytest.fixture()
def mc(lu, monkeypatch, stub_git):
    fake = FakeMC()
    monkeypatch.setattr(lu, "_mc", fake)
    return fake


def test_upload_project_uploads_manifest_plus_metadata(lu, repo, mc):
    result = lu.upload_project("demo", repo)

    assert sorted(mc.cp_targets()) == sorted([
        "README.md",
        "REPORT.md",
        str(Path("data/results.csv")),
        "project_metadata.json",
    ])
    assert result["status"] == "ok"
    assert result["local_files"] == 3
    assert result["remote_files"] == 4
    assert result["remote_path"].endswith("/projects/demo/")
    assert result["s3a_path"] == f"{lu.S3A_BASE}/demo/"
    assert isinstance(result["duration_seconds"], float)


def test_upload_project_removes_generated_metadata_afterwards(lu, repo, mc):
    lu.upload_project("demo", repo)
    assert not (repo / "projects" / "demo" / "project_metadata.json").exists()


def test_upload_project_removes_metadata_even_when_upload_fails(lu, repo, monkeypatch, stub_git):
    """The `finally` cleanup must run on the failure path too.

    A leftover project_metadata.json pollutes git status and would be picked up
    by the next run's manifest walk.
    """
    monkeypatch.setattr(lu, "_mc", FakeMC(cp_failures={"README.md"}))
    assert lu.upload_project("demo", repo) is None
    assert not (repo / "projects" / "demo" / "project_metadata.json").exists()


def test_upload_project_does_not_upload_submit_lock(lu, repo, mc):
    """/submit holds .submit.lock through Phase 3 — it must not reach the archive."""
    (repo / "projects" / "demo" / ".submit.lock").write_text("held")
    lu.upload_project("demo", repo)
    assert ".submit.lock" not in mc.cp_targets()


def test_upload_project_missing_project_returns_none(lu, repo, mc):
    assert lu.upload_project("nope", repo) is None
    assert mc.calls == []


def test_upload_project_bails_when_alias_unconfigured(lu, repo, monkeypatch, stub_git):
    fake = FakeMC(alias_ok=False)
    monkeypatch.setattr(lu, "_mc", fake)
    assert lu.upload_project("demo", repo) is None
    assert fake.verbs() == ["alias"]


# --- upload_project: re-submission contamination guard ---------------------


def test_first_upload_does_not_call_rm(lu, repo, mc):
    """An empty prefix (`mc ls` rc != 0) is normal on a first submission."""
    lu.upload_project("demo", repo)
    assert "rm" not in mc.verbs()


def test_resubmit_clears_stale_prefix_before_uploading(lu, repo, monkeypatch, stub_git):
    """`mc cp` overlays but never deletes, so a re-submit that drops a file
    would leave the stale object behind. The pre-clear is what guarantees the
    archive holds only the current approved manifest."""
    fake = FakeMC(prepopulated=["README.md", "data/dropped.csv", "project_metadata.json"])
    monkeypatch.setattr(lu, "_mc", fake)

    result = lu.upload_project("demo", repo)

    verbs = fake.verbs()
    assert verbs.index("rm") < verbs.index("cp"), "clear must precede the first cp"
    assert result["status"] == "ok"
    assert "data/dropped.csv" not in fake.remote


def test_resubmit_aborts_when_clear_fails(lu, repo, monkeypatch, stub_git):
    """A failed clear must abort rather than mix new files into a stale archive."""
    fake = FakeMC(prepopulated=["README.md"], rm_rc=1)
    monkeypatch.setattr(lu, "_mc", fake)

    assert lu.upload_project("demo", repo) is None
    assert "cp" not in fake.verbs()
    assert not (repo / "projects" / "demo" / "project_metadata.json").exists()


# --- upload_project: failure + partial-upload accounting -------------------


def test_cp_failure_returns_none(lu, repo, monkeypatch, stub_git):
    monkeypatch.setattr(lu, "_mc", FakeMC(cp_failures={str(Path("data/results.csv"))}))
    assert lu.upload_project("demo", repo) is None


def test_partial_upload_is_warning_not_ok(lu, repo, monkeypatch, stub_git):
    """A file that silently fails to land must not pass as `ok`.

    The check is `remote_count >= len(manifest) + 1`; without the +1 for
    project_metadata.json, one lost project file would still satisfy
    `>= len(manifest)` and an incomplete archive would be marked ok. Here cp
    reports success but the object never appears remotely.
    """
    monkeypatch.setattr(lu, "_mc", LosesAFile())
    result = lu.upload_project("demo", repo)

    assert result["status"] == "warning"
    assert result["local_files"] == 3
    assert result["remote_files"] == 3  # 2 manifest files + metadata


# --- upload_project: context mirror wiring ---------------------------------


def test_mirror_off_by_default(lu, repo, mc, monkeypatch):
    called = []
    monkeypatch.setattr(lu, "submit_to_context_service", lambda *a: called.append(a))
    result = lu.upload_project("demo", repo)
    assert called == []
    assert "context_submission" not in result


def test_mirror_runs_on_clean_upload_when_requested(lu, repo, mc, monkeypatch):
    monkeypatch.setattr(
        lu, "submit_to_context_service",
        lambda pid, base: {"status": "ok", "reason": "ingested"},
    )
    result = lu.upload_project("demo", repo, mirror_to_context=True)
    assert result["context_submission"] == {"status": "ok", "reason": "ingested"}


def test_mirror_skipped_on_partial_upload(lu, repo, monkeypatch, stub_git):
    """A `warning` archive is incomplete — there is nothing trustworthy to mirror."""
    called = []
    monkeypatch.setattr(lu, "_mc", LosesAFile())
    monkeypatch.setattr(lu, "submit_to_context_service", lambda *a: called.append(a))

    result = lu.upload_project("demo", repo, mirror_to_context=True)
    assert result["status"] == "warning"
    assert called == []
    assert "context_submission" not in result


# --- upload_all_projects ---------------------------------------------------


@pytest.fixture()
def multi_repo(repo: Path) -> Path:
    for name in ("alpha", "zeta"):
        p = repo / "projects" / name
        p.mkdir()
        (p / "README.md").write_text(f"# {name}\n")
    (repo / "projects" / ".hidden").mkdir()
    (repo / "projects" / "loose_file.md").write_text("not a project\n")
    return repo


def test_upload_all_visits_every_project_sorted(lu, multi_repo, monkeypatch, stub_git):
    seen = []
    monkeypatch.setattr(lu, "_check_mc_alias", lambda: True)
    monkeypatch.setattr(
        lu, "upload_project",
        lambda pid, base: seen.append(pid) or {
            "project_id": pid, "remote_files": 1, "total_size_bytes": 1,
            "local_files": 1, "status": "ok",
        },
    )
    results = lu.upload_all_projects(multi_repo)

    assert seen == ["alpha", "demo", "zeta"], "hidden dirs and loose files excluded"
    assert len(results) == 3


def test_upload_all_never_mirrors_to_context(lu, multi_repo, monkeypatch, stub_git):
    """Batch uploads must not trigger a re-ingest — only /submit's single
    upload does. upload_project is called positionally, so mirror_to_context
    stays at its False default."""
    kwargs_seen = []
    monkeypatch.setattr(lu, "_check_mc_alias", lambda: True)

    def fake_upload(pid, base, **kwargs):
        kwargs_seen.append(kwargs)
        return {"project_id": pid, "remote_files": 1, "total_size_bytes": 1,
                "local_files": 1, "status": "ok"}

    monkeypatch.setattr(lu, "upload_project", fake_upload)
    lu.upload_all_projects(multi_repo)
    assert all(not kw.get("mirror_to_context") for kw in kwargs_seen)


def test_upload_all_drops_failed_projects(lu, multi_repo, monkeypatch, stub_git):
    monkeypatch.setattr(lu, "_check_mc_alias", lambda: True)
    monkeypatch.setattr(
        lu, "upload_project",
        lambda pid, base: None if pid == "demo" else {
            "project_id": pid, "remote_files": 1, "total_size_bytes": 1,
            "local_files": 1, "status": "ok",
        },
    )
    results = lu.upload_all_projects(multi_repo)
    assert [r["project_id"] for r in results] == ["alpha", "zeta"]


def test_upload_all_bails_without_alias(lu, multi_repo, monkeypatch):
    monkeypatch.setattr(lu, "_check_mc_alias", lambda: False)
    assert lu.upload_all_projects(multi_repo) == []


# --- validate_uploads ------------------------------------------------------


@pytest.mark.parametrize(
    "prepopulated,expected",
    [
        ([], "NOT UPLOADED"),
        (["README.md"], "MISMATCH"),
        (["README.md", "REPORT.md", "data/results.csv", "project_metadata.json"], "OK"),
    ],
)
def test_validate_uploads_reports_status(lu, repo, monkeypatch, capsys, prepopulated, expected):
    monkeypatch.setattr(lu, "_mc", FakeMC(prepopulated=prepopulated))
    lu.validate_uploads(repo)
    line = next(l for l in capsys.readouterr().out.splitlines() if l.startswith("demo"))
    assert line.split()[-1] == expected.split()[-1]
    assert expected in line


# --- main(): CLI contract --------------------------------------------------


def _run_main(lu, monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["lakehouse_upload.py"] + argv)
    with pytest.raises(SystemExit) as exc:
        lu.main()
    return exc.value.code


def test_main_success_emits_json_and_exits_zero(lu, repo, monkeypatch, capsys):
    monkeypatch.setattr(
        lu, "upload_project",
        lambda pid, base, mirror_to_context=False: {
            "project_id": pid, "s3a_path": "s3a://cdm-lake/t/projects/demo/",
            "remote_files": 4, "total_size_bytes": 123, "local_files": 3,
            "duration_seconds": 1.5, "status": "ok",
        },
    )
    code = _run_main(lu, monkeypatch, ["demo", "--base-path", str(repo)])
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert code == 0
    assert payload == {
        "archive_key": "s3a://cdm-lake/t/projects/demo/",
        "file_count": 4,
        "byte_total": 123,
        "duration_seconds": 1.5,
    }


def test_main_partial_upload_exits_two_with_error_field(lu, repo, monkeypatch, capsys):
    """Exit 2 = archive exists but is incomplete; the caller writes
    SUBMISSION_FAILED.md. The count in the message subtracts the generated
    project_metadata.json so it reflects local manifest files that landed."""
    monkeypatch.setattr(
        lu, "upload_project",
        lambda pid, base, mirror_to_context=False: {
            "project_id": pid, "s3a_path": "s3a://cdm-lake/t/projects/demo/",
            "remote_files": 3, "total_size_bytes": 123, "local_files": 3,
            "duration_seconds": 1.5, "status": "warning",
        },
    )
    code = _run_main(lu, monkeypatch, ["demo", "--base-path", str(repo)])
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert code == 2
    assert payload["archive_key"] == "s3a://cdm-lake/t/projects/demo/"
    assert payload["error"] == "partial upload: 2 of 3 local files present at archive_key"


def test_main_hard_failure_exits_one_without_json(lu, repo, monkeypatch, capsys):
    monkeypatch.setattr(lu, "upload_project", lambda *a, **kw: None)
    code = _run_main(lu, monkeypatch, ["demo", "--base-path", str(repo)])
    assert code == 1
    assert capsys.readouterr().out.strip() == ""


def test_main_mirror_on_by_default_and_off_with_flag(lu, repo, monkeypatch, capsys):
    seen = {}
    monkeypatch.setattr(
        lu, "upload_project",
        lambda pid, base, mirror_to_context=False: seen.update(mirror=mirror_to_context) or {
            "project_id": pid, "s3a_path": "s3a://x/", "remote_files": 1,
            "total_size_bytes": 1, "local_files": 0, "duration_seconds": 0.1,
            "status": "ok",
        },
    )

    _run_main(lu, monkeypatch, ["demo", "--base-path", str(repo)])
    assert seen["mirror"] is True

    _run_main(lu, monkeypatch, ["demo", "--base-path", str(repo), "--no-context-mirror"])
    assert seen["mirror"] is False


def test_main_context_submission_is_advisory_only(lu, repo, monkeypatch, capsys):
    """A failed mirror on a clean archive still exits 0 — the lakehouse, not the
    context index, is the source of truth for 'submitted'."""
    monkeypatch.setattr(
        lu, "upload_project",
        lambda pid, base, mirror_to_context=False: {
            "project_id": pid, "s3a_path": "s3a://x/", "remote_files": 1,
            "total_size_bytes": 1, "local_files": 0, "duration_seconds": 0.1,
            "status": "ok",
            "context_submission": {"status": "failed", "reason": "ov down"},
        },
    )
    code = _run_main(lu, monkeypatch, ["demo", "--base-path", str(repo)])
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert code == 0
    assert payload["context_submission"] == {"status": "failed", "reason": "ov down"}


def test_main_tenant_override_retargets_paths(lu, repo, monkeypatch, capsys):
    """Path-consuming functions read the module globals at call time, so the
    override must be visible to upload_project by the time it runs."""
    captured = {}

    def fake_upload(pid, base, mirror_to_context=False):
        captured["s3a_base"] = lu.S3A_BASE
        captured["lakehouse_base"] = lu.LAKEHOUSE_BASE
        return {"project_id": pid, "s3a_path": f"{lu.S3A_BASE}/{pid}/",
                "remote_files": 1, "total_size_bytes": 1, "local_files": 0,
                "duration_seconds": 0.1, "status": "ok"}

    monkeypatch.setattr(lu, "upload_project", fake_upload)
    _run_main(
        lu, monkeypatch,
        ["demo", "--base-path", str(repo), "--tenant-path", "tenant-general-warehouse/nmdc"],
    )

    assert captured["s3a_base"] == "s3a://cdm-lake/tenant-general-warehouse/nmdc/projects"
    assert captured["lakehouse_base"].endswith(
        "cdm-lake/tenant-general-warehouse/nmdc/projects"
    )


def test_main_tenant_override_reads_env(lu, repo, monkeypatch, capsys):
    monkeypatch.setenv("BERIL_UPLOAD_TENANT_PATH", "tenant-general-warehouse/nmdc")
    monkeypatch.setattr(lu, "list_projects", lambda: print(lu.S3A_BASE))
    monkeypatch.setattr(sys, "argv", ["lakehouse_upload.py", "--list"])
    lu.main()
    assert "tenant-general-warehouse/nmdc" in capsys.readouterr().out


def test_main_no_args_prints_help(lu, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["lakehouse_upload.py"])
    lu.main()
    assert "usage:" in capsys.readouterr().out
