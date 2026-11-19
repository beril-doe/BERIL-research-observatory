"""Tests for the submission record (`observatory_context.beril_submit`).

The record is what the wiki feed is built from: a manifest of every archived
file plus a bundle of the text files, then one PUT per embedded figure. These
run against a stubbed transport; no BERIL instance is involved.
"""

from __future__ import annotations

import hashlib
import io
import json
import zipfile

import httpx
import pytest

from observatory_context import beril_submit
from observatory_context.beril_submit import (
    BerilSubmitError,
    build_bundle,
    build_manifest,
    embedded_figures,
    file_entries,
    is_bundle_file,
    post_record,
    put_file,
    submit_record,
)

BASE_URL = "https://beril.test"
OWNER = "0009-0001-2345-6789"
APPROVAL = {"by": OWNER, "at": "2026-11-01T00:00:00Z", "report_hash": "sha256:" + "ab" * 32}
PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(16))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "projects" / "alpha"
    (root / "figures").mkdir(parents=True)
    (root / "data").mkdir()
    (root / "REPORT.md").write_text(
        "# Report\n\n![fig](figures/fig1.png)\n\n<img src=\"figures/fig2.png\">\n"
        "![remote](https://x.test/a.png) ![missing](figures/nope.png)\n"
    )
    (root / "README.md").write_text("# Alpha\n")
    (root / "beril.yaml").write_text("project_id: alpha\n")
    (root / "REFUTATION_1.md").write_text("refuted\n")
    (root / "figures" / "fig1.png").write_bytes(PNG)
    (root / "figures" / "fig2.png").write_bytes(PNG[::-1])
    (root / "data" / "results.csv").write_text("a,b\n")
    (root / ".submit.lock").write_text("")
    return root


def _files(root):
    return file_entries(
        root, [p for p in sorted(root.rglob("*")) if p.is_file() and p.name != ".submit.lock"]
    )


class FakeServer:
    """Answers POST /api/context/submissions and the per-file PUT, recording
    requests. ``missing`` is what the post reports; each PUT whose body hashes
    to the manifest entry removes its path, a mismatch answers 409."""

    def __init__(self, *, missing=(), sid="sub-1", post_status=None):
        self.requests: list[httpx.Request] = []
        self.missing = list(missing)
        self.sid = sid
        self.manifest = None
        self.bundle_names = None
        self.post_status = post_status

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.method == "POST":
            body = request.read()
            self.manifest, self.bundle_names = _parse_multipart(body, request.headers["Content-Type"])
            if self.post_status:
                return httpx.Response(self.post_status, json={"detail": "refused"})
            status = "complete" if not self.missing else "pending"
            return httpx.Response(200, json={"id": self.sid, "status": status, "missing": self.missing})
        if request.method == "PUT":
            rel = request.url.path.split(f"/files/", 1)[1]
            want = {f["path"]: f["sha256"] for f in self.manifest["files"]}.get(rel)
            if _sha(request.read()) != want:
                return httpx.Response(409, json={"detail": f"sha256 mismatch for {rel}"})
            self.missing = [m for m in self.missing if m != rel]
            status = "complete" if not self.missing else "pending"
            return httpx.Response(200, json={"status": status, "missing": self.missing})
        return httpx.Response(404)

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self), base_url=BASE_URL,
                            headers={"Authorization": "Bearer pat"})


def _parse_multipart(body: bytes, content_type: str):
    boundary = content_type.split("boundary=", 1)[1].encode()
    manifest = None
    names = None
    for part in body.split(b"--" + boundary):
        if b"\r\n\r\n" not in part:
            continue
        head, _, data = part.partition(b"\r\n\r\n")
        data = data.rstrip(b"\r\n").removesuffix(b"--")
        if b'name="manifest.json"' in head:
            manifest = json.loads(data)
        elif b'name="bundle.zip"' in head:
            names = sorted(zipfile.ZipFile(io.BytesIO(data)).namelist())
    return manifest, names


# --- pieces ----------------------------------------------------------------


def test_embedded_figures_finds_markdown_and_html_images_once_each():
    text = (
        "![a](figures/a.png) ![b](./figures/b.png \"title\")\n<IMG src='figures/c.png'>\n"
        "![a again](figures/a.png) ![url](https://x/y.png) ![abs](/etc/x.png)\n"
    )
    assert embedded_figures(text) == ["figures/a.png", "figures/b.png", "figures/c.png"]


@pytest.mark.parametrize(
    ("path", "bundled"),
    [("REPORT.md", True), ("README.md", True), ("beril.yaml", True), ("CORRECTIONS.md", True),
     ("REFUTATION_2.md", True), ("RESEARCH_PLAN.md", False), ("figures/x.png", False),
     ("memories/REPORT.md", False)],
)
def test_bundle_allowlist(path, bundled):
    assert is_bundle_file(path) is bundled


def test_file_entries_hash_every_file_with_posix_paths(project):
    entries = _files(project)
    assert [e["path"] for e in entries] == [
        "README.md", "REFUTATION_1.md", "REPORT.md", "beril.yaml",
        "data/results.csv", "figures/fig1.png", "figures/fig2.png",
    ]
    fig = next(e for e in entries if e["path"] == "figures/fig1.png")
    assert fig == {"path": "figures/fig1.png", "sha256": _sha(PNG), "size": len(PNG)}


def test_manifest_revision_is_the_report_sha256_and_approval_is_unprefixed(project):
    files = _files(project)
    manifest = build_manifest(
        project="alpha", owner_orcid=OWNER, archive_path="s3a://b/p/alpha/",
        approval=APPROVAL, files=files, submitted_at="2026-11-02T00:00:00Z",
    )
    assert manifest["revision"] == _sha((project / "REPORT.md").read_bytes())
    assert manifest["approval"] == {"by": OWNER, "at": APPROVAL["at"], "report_hash": "ab" * 32}
    assert manifest["submitted_at"] == "2026-11-02T00:00:00Z"
    assert manifest["files"] == files
    with pytest.raises(ValueError, match="REPORT.md"):
        build_manifest(project="alpha", owner_orcid=OWNER, archive_path="x", approval=APPROVAL,
                       files=[f for f in files if f["path"] != "REPORT.md"])


def test_bundle_holds_only_the_allowlisted_text_files(project):
    data, names = build_bundle(project, _files(project))
    assert names == ["README.md", "REFUTATION_1.md", "REPORT.md", "beril.yaml"]
    archive = zipfile.ZipFile(io.BytesIO(data))
    assert sorted(archive.namelist()) == sorted(names)
    assert archive.read("REFUTATION_1.md") == b"refuted\n"


# --- wire ------------------------------------------------------------------


def test_post_record_sends_manifest_and_bundle_as_multipart(project):
    server = FakeServer()
    files = _files(project)
    manifest = build_manifest(project="alpha", owner_orcid=OWNER, archive_path="s3a://x/",
                              approval=APPROVAL, files=files)
    bundle, _ = build_bundle(project, files)

    with server.client() as client:
        receipt = post_record(client, manifest, bundle)

    request = server.requests[0]
    assert request.url.path == "/api/context/submissions"
    assert request.headers["Authorization"] == "Bearer pat"
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert server.manifest == manifest
    assert server.bundle_names == ["README.md", "REFUTATION_1.md", "REPORT.md", "beril.yaml"]
    assert (receipt.id, receipt.status, receipt.missing) == ("sub-1", "complete", [])


def test_put_file_sends_raw_bytes_to_the_per_file_route(project):
    server = FakeServer(missing=["figures/fig1.png"])
    files = _files(project)
    with server.client() as client:
        post_record(client, build_manifest(project="alpha", owner_orcid=OWNER, archive_path="x",
                                           approval=APPROVAL, files=files),
                    build_bundle(project, files)[0])
        receipt = put_file(client, "sub-1", "figures/fig1.png", PNG)

    put = server.requests[-1]
    assert put.method == "PUT"
    assert put.url.path == "/api/context/submissions/sub-1/files/figures/fig1.png"
    assert put.headers["Content-Type"] == "application/octet-stream"
    assert put.read() == PNG
    assert receipt.status == "complete" and receipt.missing == []


def test_submit_record_puts_only_the_embedded_figures_the_server_lacks(project):
    server = FakeServer(missing=["figures/fig1.png", "figures/fig2.png", "data/results.csv"])

    with server.client() as client:
        outcome = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                                archive_path="s3a://x/", approval=APPROVAL, files=_files(project))

    puts = [r.url.path.split("/files/")[1] for r in server.requests if r.method == "PUT"]
    assert puts == ["figures/fig1.png", "figures/fig2.png"]
    # data/results.csv is archived but not embedded, so the record stays
    # pending and says what is missing.
    assert outcome.status == "failed" and outcome.id == "sub-1"
    assert outcome.missing == ["data/results.csv"] and "data/results.csv" in outcome.reason


def test_submit_record_is_ok_once_the_server_says_complete(project):
    server = FakeServer(missing=["figures/fig1.png", "figures/fig2.png"])

    with server.client() as client:
        outcome = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                                archive_path="s3a://x/", approval=APPROVAL, files=_files(project))

    assert outcome.status == "ok" and outcome.id == "sub-1" and outcome.missing == []
    assert outcome.revision == _sha((project / "REPORT.md").read_bytes())
    assert outcome.as_dict()["status"] == "ok"


def test_submit_record_skips_puts_when_the_post_is_already_complete(project):
    server = FakeServer()
    with server.client() as client:
        outcome = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                                archive_path="s3a://x/", approval=APPROVAL, files=_files(project))
    assert [r.method for r in server.requests] == ["POST"]
    assert outcome.status == "ok"


def test_re_posting_the_same_revision_is_idempotent(project):
    """The server keys on (owner, project, revision); a second post gets the
    same id and nothing else changes on our side."""
    server = FakeServer()
    files = _files(project)
    with server.client() as client:
        first = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                              archive_path="s3a://x/", approval=APPROVAL, files=files)
        second = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                               archive_path="s3a://x/", approval=APPROVAL, files=files)
    posts = [r for r in server.requests if r.method == "POST"]
    assert len(posts) == 2
    assert first.id == second.id == "sub-1" and first.revision == second.revision
    assert second.status == "ok"


def test_a_figure_sha_mismatch_is_a_failed_outcome_not_an_exception(project):
    """The manifest says one thing and the bytes another (the file changed
    between archive and record): the server refuses, the outcome says so."""
    server = FakeServer(missing=["figures/fig1.png"])
    files = _files(project)
    (project / "figures" / "fig1.png").write_bytes(b"changed")

    with server.client() as client:
        outcome = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                                archive_path="s3a://x/", approval=APPROVAL, files=files)

    assert outcome.status == "failed" and outcome.revision
    assert "409" in outcome.reason and "sha256 mismatch for figures/fig1.png" in outcome.reason


def test_a_refused_post_is_a_failed_outcome(project):
    server = FakeServer(post_status=403)
    with server.client() as client:
        outcome = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                                archive_path="s3a://x/", approval=APPROVAL, files=_files(project))
    assert outcome.status == "failed" and "403" in outcome.reason and outcome.id is None


def test_an_unreachable_server_is_a_failed_outcome(project):
    def down(request):
        raise httpx.ConnectError("refused")
    client = httpx.Client(transport=httpx.MockTransport(down), base_url=BASE_URL)
    outcome = submit_record(client, project, project="alpha", owner_orcid=OWNER,
                            archive_path="s3a://x/", approval=APPROVAL, files=_files(project))
    assert outcome.status == "failed" and "could not reach" in outcome.reason


def test_post_record_raises_with_status_and_detail(project):
    def handler(request):
        return httpx.Response(422, json={"detail": "approval.by is not the caller"})
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE_URL)
    with pytest.raises(BerilSubmitError) as info:
        post_record(client, {"project": "alpha"}, b"")
    assert info.value.status == 422 and "approval.by is not the caller" in str(info.value)


def test_client_for_carries_base_url_and_token():
    with beril_submit.client_for("https://beril.test/", "pat") as client:
        assert str(client.base_url) == "https://beril.test"
        assert client.headers["Authorization"] == "Bearer pat"


# --- the record kept for a retry ---------------------------------------------


def test_record_paths_are_the_bundle_files_and_the_embedded_figures_listed(project):
    files = _files(project)
    report = (project / "REPORT.md").read_text()
    assert beril_submit.record_paths(files, report) == [
        "README.md", "REFUTATION_1.md", "REPORT.md", "beril.yaml",
        "figures/fig1.png", "figures/fig2.png",
    ]  # not data/, not the unlisted figures/nope.png


def test_a_kept_record_round_trips_and_holds_only_what_it_sends(project, tmp_path):
    files = _files(project)
    state = tmp_path / "state"

    kept = beril_submit.save_pending(
        state, "alpha", project, files=files, archive_path="s3a://b/alpha/",
        submitted_at="2026-11-02T00:00:00+00:00",
    )

    again = beril_submit.load_pending(state, "alpha")
    assert again == kept
    assert (again.files, again.archive_path, again.submitted_at) == (
        files, "s3a://b/alpha/", "2026-11-02T00:00:00+00:00"
    )
    held = sorted(p.relative_to(again.root).as_posix() for p in again.root.rglob("*") if p.is_file())
    assert held == beril_submit.record_paths(files, (project / "REPORT.md").read_text())
    assert (again.root / "figures" / "fig1.png").read_bytes() == PNG


def test_a_kept_record_ignores_later_edits_to_the_project(project, tmp_path):
    state = tmp_path / "state"
    beril_submit.save_pending(state, "alpha", project, files=_files(project),
                              archive_path="s3a://b/alpha/")
    (project / "README.md").write_text("edited after archiving\n")
    (project / "figures" / "fig1.png").write_bytes(b"edited")

    kept = beril_submit.load_pending(state, "alpha")
    assert (kept.root / "README.md").read_text() == "# Alpha\n"
    assert (kept.root / "figures" / "fig1.png").read_bytes() == PNG


def test_saving_again_replaces_the_kept_record_and_drop_forgets_it(project, tmp_path):
    state = tmp_path / "state"
    beril_submit.save_pending(state, "alpha", project, files=_files(project),
                              archive_path="s3a://b/old/")
    beril_submit.save_pending(state, "alpha", project, files=_files(project),
                              archive_path="s3a://b/new/")
    assert beril_submit.load_pending(state, "alpha").archive_path == "s3a://b/new/"
    assert sorted(p.name for p in (state / beril_submit.PENDING_DIR).iterdir()) == ["alpha"]

    beril_submit.drop_pending(state, "alpha")
    assert beril_submit.load_pending(state, "alpha") is None
    assert beril_submit.load_pending(state, "never-kept") is None


@pytest.mark.parametrize("bad", ["", ".", "..", "a/b", "a\\b"])
def test_a_kept_record_needs_a_plain_project_id(bad, tmp_path):
    with pytest.raises(ValueError):
        beril_submit.load_pending(tmp_path, bad)


def test_submit_pending_sends_the_kept_record_as_the_owner_given(project, tmp_path):
    state = tmp_path / "state"
    kept = beril_submit.save_pending(
        state, "alpha", project, files=_files(project), archive_path="s3a://b/alpha/",
        submitted_at="2026-11-02T00:00:00+00:00",
    )
    server = FakeServer()
    with server.client() as client:
        outcome = beril_submit.submit_pending(client, kept, owner_orcid=OWNER, approval=APPROVAL)
    assert outcome.status == "ok"
    manifest = server.manifest
    assert manifest["owner_orcid"] == OWNER and manifest["files"] == kept.files
    assert manifest["submitted_at"] == "2026-11-02T00:00:00+00:00"


def test_the_approval_is_read_from_the_kept_beril_yaml(project, tmp_path):
    (project / "beril.yaml").write_text(
        "project_id: alpha\napproval:\n  by: \"x\"\n  at: \"2026-11-01T00:00:00Z\"\n"
    )
    kept = beril_submit.save_pending(tmp_path, "alpha", project, files=_files(project),
                                     archive_path="s3a://b/alpha/")
    (project / "beril.yaml").write_text("project_id: alpha\n")  # edited after archiving
    assert beril_submit.kept_approval(kept) == {"by": "x", "at": "2026-11-01T00:00:00Z"}
    (kept.root / "beril.yaml").write_text("- not a mapping\n")
    assert beril_submit.kept_approval(kept) == {}
