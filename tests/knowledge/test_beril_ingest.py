"""Tests for the BERIL-route context mirror (`observatory_context.beril_ingest`).

These exercise the archive/manifest wire format and the polling loop against a
stubbed transport — no BERIL instance and no OpenViking are involved.
"""

from __future__ import annotations

import io
import zipfile

import httpx
import pytest

from observatory_context.beril_ingest import (
    BerilIngestError,
    build_archive,
    ingest_project_files,
    poll_batch,
    submit_ingest,
)

BASE_URL = "https://beril.test"
TOKEN = "pat-token"


def _project(tmp_path, files=None):
    """Write a small staged project tree; return (root, file list)."""
    files = files or {"REPORT.md": "report", "memories/pitfalls.md": "pitfall"}
    root = tmp_path / "staged"
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root, sorted(p for p in root.rglob("*") if p.is_file())


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE_URL)


def _status_body(status, files, counts=None):
    return {
        "batch_id": "batch-1",
        "project": "proj",
        "status": status,
        "counts": counts or {},
        "files": files,
    }


# --- build_archive ---------------------------------------------------------


def test_build_archive_preserves_nested_paths(tmp_path):
    root, files = _project(tmp_path)
    archive, manifest = build_archive(root, files)

    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        names = sorted(zf.namelist())
    # The nested path is what a flat multipart upload would have lost.
    assert names == ["REPORT.md", "memories/pitfalls.md"]
    assert manifest == names


def test_build_archive_manifest_matches_members(tmp_path):
    root, files = _project(tmp_path, {"a.md": "a", "b/c.md": "c", "b/d/e.md": "e"})
    archive, manifest = build_archive(root, files)

    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        assert sorted(zf.namelist()) == sorted(manifest)
        assert zf.read("b/d/e.md") == b"e"


def test_build_archive_rejects_file_outside_root(tmp_path):
    root, files = _project(tmp_path)
    outside = tmp_path / "elsewhere.md"
    outside.write_text("x", encoding="utf-8")

    with pytest.raises(BerilIngestError, match="outside the staged project root"):
        build_archive(root, files + [outside])


def test_build_archive_rejects_empty_file_list(tmp_path):
    root, _ = _project(tmp_path)
    with pytest.raises(BerilIngestError, match="No files to ingest"):
        build_archive(root, [])


# --- submit_ingest ---------------------------------------------------------


def test_submit_ingest_posts_archive_manifest_and_project(tmp_path):
    root, files = _project(tmp_path)
    archive, manifest = build_archive(root, files)
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("Authorization")
        seen["body"] = request.content
        return httpx.Response(200, json={"batch_id": "batch-1", "queued": 2, "failed": 0})

    with _client(handler) as http:
        body = submit_ingest(
            BASE_URL,
            TOKEN,
            project="proj",
            archive=archive,
            manifest=manifest,
            client=http,
        )

    assert body["batch_id"] == "batch-1"
    assert seen["url"] == f"{BASE_URL}/api/context/ingest_files"
    assert seen["auth"] == f"Bearer {TOKEN}"
    # Multipart carries all three parts the route requires.
    assert b'name="project"' in seen["body"]
    assert b'name="archive"' in seen["body"]
    assert b'name="manifest"' in seen["body"]
    # The manifest travels as newline-separated relative paths.
    assert b"memories/pitfalls.md" in seen["body"]


def test_submit_ingest_surfaces_server_detail(tmp_path):
    root, files = _project(tmp_path)
    archive, manifest = build_archive(root, files)

    def handler(request):
        return httpx.Response(400, json={"detail": "not a zip file"})

    with _client(handler) as http:
        with pytest.raises(BerilIngestError, match="400.*not a zip file"):
            submit_ingest(
                BASE_URL, TOKEN, project="p", archive=archive, manifest=manifest, client=http
            )


# --- poll_batch ------------------------------------------------------------


def test_poll_batch_returns_on_completion():
    bodies = [
        _status_body("processing", [{"relative_path": "a.md", "status": "queued"}]),
        _status_body(
            "completed",
            [{"relative_path": "a.md", "status": "completed"}],
            counts={"completed": 1},
        ),
    ]
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(200, json=bodies[min(len(calls) - 1, len(bodies) - 1)])

    with _client(handler) as http:
        outcome = poll_batch(
            BASE_URL, TOKEN, "batch-1", client=http, interval=0, sleep=lambda _: None
        )

    assert outcome.ok
    assert outcome.status == "completed"
    assert len(calls) == 2
    assert calls[0] == f"{BASE_URL}/api/context/ingest_status/batch-1"


def test_poll_batch_stops_on_failure_with_reasons():
    body = _status_body(
        "failed",
        [
            {"relative_path": "a.md", "status": "completed"},
            {"relative_path": "b.md", "status": "failed", "error": "rejected"},
        ],
        counts={"completed": 1, "failed": 1},
    )

    with _client(lambda r: httpx.Response(200, json=body)) as http:
        outcome = poll_batch(
            BASE_URL, TOKEN, "batch-1", client=http, interval=0, sleep=lambda _: None
        )

    assert not outcome.ok
    assert not outcome.timed_out
    assert outcome.failures == [("b.md", "rejected")]
    assert "b.md: rejected" in outcome.summary()


def test_poll_batch_times_out_without_failing():
    """An unfinished batch is not a failure — the files may still land."""
    body = _status_body(
        "processing",
        [{"relative_path": "a.md", "status": "queued"}],
        counts={"queued": 1},
    )
    clock = iter([0.0, 0.0, 1.0, 99.0, 99.0, 99.0])

    with _client(lambda r: httpx.Response(200, json=body)) as http:
        outcome = poll_batch(
            BASE_URL,
            TOKEN,
            "batch-1",
            client=http,
            interval=0,
            max_wait=10,
            sleep=lambda _: None,
            monotonic=lambda: next(clock),
        )

    assert not outcome.ok
    assert outcome.timed_out
    assert "still in flight" in outcome.summary()


def test_poll_batch_retries_through_a_transport_blip():
    """A blip mid-poll keeps polling — the batch is queued server-side."""
    responses = [
        httpx.Response(503, text="upstream down"),
        httpx.Response(
            200,
            json=_status_body(
                "completed",
                [{"relative_path": "a.md", "status": "completed"}],
                counts={"completed": 1},
            ),
        ),
    ]
    calls = []

    def handler(request):
        calls.append(1)
        return responses[min(len(calls) - 1, len(responses) - 1)]

    with _client(handler) as http:
        outcome = poll_batch(
            BASE_URL, TOKEN, "batch-1", client=http, interval=0, sleep=lambda _: None
        )

    assert outcome.ok
    assert len(calls) == 2


# --- ingest_project_files --------------------------------------------------


def test_ingest_project_files_submits_then_polls(tmp_path):
    root, files = _project(tmp_path)
    seen = []

    def handler(request):
        seen.append(request.url.path)
        if request.url.path.endswith("/ingest_files"):
            return httpx.Response(200, json={"batch_id": "b7", "queued": 2, "failed": 0})
        return httpx.Response(
            200,
            json=_status_body(
                "completed",
                [{"relative_path": "REPORT.md", "status": "completed"}],
                counts={"completed": 2},
            ),
        )

    with _client(handler) as http:
        outcome = ingest_project_files(
            BASE_URL,
            TOKEN,
            project="proj",
            root=root,
            files=files,
            client=http,
            interval=0,
            sleep=lambda _: None,
        )

    assert outcome.ok
    assert outcome.batch_id == "b7"
    assert seen == ["/api/context/ingest_files", "/api/context/ingest_status/b7"]


def test_ingest_project_files_errors_without_a_batch_id(tmp_path):
    """A submission we cannot follow is an error — files were accepted but
    no handle came back to poll them with."""
    root, files = _project(tmp_path)

    def handler(request):
        return httpx.Response(200, json={"queued": 2, "failed": 0})

    with _client(handler) as http:
        with pytest.raises(BerilIngestError, match="no batch_id"):
            ingest_project_files(
                BASE_URL, TOKEN, project="proj", root=root, files=files, client=http
            )


def test_ingest_project_files_treats_all_skipped_as_success(tmp_path):
    """Every file already current: no batch, nothing polled, still ok.

    The server sends no batch_id when it submitted nothing, so this must not be
    mistaken for a submission that lost its handle.
    """
    root, files = _project(tmp_path)
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(
            200, json={"batch_id": None, "queued": 0, "failed": 0, "skipped": 2}
        )

    with _client(handler) as http:
        outcome = ingest_project_files(
            BASE_URL, TOKEN, project="proj", root=root, files=files, client=http
        )

    assert outcome.ok
    assert outcome.batch_id is None
    assert outcome.skipped == 2
    # Nothing to poll, so the status endpoint is never touched.
    assert calls == ["/api/context/ingest_files"]
    assert "already current" in outcome.summary()


def test_ingest_project_files_carries_skips_across_a_poll(tmp_path):
    """A mixed batch: skips come from the submission, not the batch status."""
    root, files = _project(tmp_path)

    def handler(request):
        if request.url.path.endswith("/ingest_files"):
            return httpx.Response(
                200, json={"batch_id": "b1", "queued": 1, "failed": 0, "skipped": 3}
            )
        return httpx.Response(
            200,
            json=_status_body(
                "completed",
                [{"relative_path": "REPORT.md", "status": "completed"}],
                counts={"completed": 1},
            ),
        )

    with _client(handler) as http:
        outcome = ingest_project_files(
            BASE_URL, TOKEN, project="proj", root=root, files=files, client=http,
            interval=0, sleep=lambda _: None,
        )

    assert outcome.ok
    assert outcome.skipped == 3
    assert outcome.summary() == "1 file(s) ingested, 3 already current"


def test_all_skipped_response_missing_the_field_is_still_success(tmp_path):
    """A server that omits `skipped` entirely still reads as a clean no-op."""
    root, files = _project(tmp_path)

    with _client(lambda r: httpx.Response(200, json={"queued": 0, "failed": 0})) as http:
        outcome = ingest_project_files(
            BASE_URL, TOKEN, project="proj", root=root, files=files, client=http
        )

    assert outcome.ok
    assert outcome.skipped == 0
