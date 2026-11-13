"""Tests for the BERIL-route file reader and submissions feed
(`observatory_context.beril_read`).

These exercise the two wire forms of ``GET /api/context/read`` (JSON envelope
and octet-stream), the sha256 verification both go through, and the
``submissions`` paging contract — against a stubbed transport. No BERIL
instance and no OpenViking are involved.
"""

from __future__ import annotations

import base64
import hashlib

import httpx
import pytest

from observatory_context.beril_read import (
    READ_PATH,
    SUBMISSIONS_PATH,
    BerilReadError,
    IntegrityError,
    list_submissions,
    read_file,
)

BASE_URL = "https://beril.test"
ADDRESS = "0009-0001-2345-6789/alpha/REPORT.md"
TEXT = "# Report\n\nA number: 42.\n"
PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(32))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _client(handler):
    return httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url=BASE_URL,
        headers={"Authorization": "Bearer pat"},
    )


def _envelope(content: str, *, encoding="utf-8", sha256=None, **extra) -> dict:
    data = base64.b64decode(content) if encoding == "base64" else content.encode("utf-8")
    body = {
        "address": ADDRESS,
        "path": "REPORT.md",
        "size": len(data),
        "sha256": sha256 if sha256 is not None else _sha(data),
        "content_type": "text/markdown",
        "encoding": encoding,
        "content": content,
        "source": "context",
        "modified_at": "2026-11-12T10:00:00Z",
    }
    body.update(extra)
    return body


def _bytes_route(data: bytes, *, sha256=None, headers=None):
    def handler(request):
        h = {
            "Content-Type": "image/png",
            "X-Content-SHA256": sha256 if sha256 is not None else _sha(data),
            "X-Content-Source": "archive",
        }
        h.update(headers or {})
        return httpx.Response(200, content=data, headers=h)
    return handler


# --- read_file: text --------------------------------------------------------


def test_text_read_asks_for_json_and_returns_the_envelope_fields():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["params"] = dict(request.url.params)
        seen["accept"] = request.headers["Accept"]
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json=_envelope(TEXT))

    with _client(handler) as client:
        file = read_file(client, ADDRESS)

    assert seen == {
        "path": READ_PATH, "params": {"address": ADDRESS},
        "accept": "application/json", "auth": "Bearer pat",
    }
    assert file.is_text and file.content == TEXT
    assert file.as_bytes() == TEXT.encode("utf-8")
    assert (file.address, file.path, file.size) == (ADDRESS, "REPORT.md", len(TEXT.encode()))
    assert file.sha256 == _sha(TEXT.encode()) and file.encoding == "utf-8"
    assert (file.content_type, file.source, file.modified_at) == (
        "text/markdown", "context", "2026-11-12T10:00:00Z",
    )


def test_text_read_verifies_the_envelope_sha256():
    def handler(request):
        return httpx.Response(200, json=_envelope(TEXT, sha256="0" * 64))

    with _client(handler) as client, pytest.raises(IntegrityError) as info:
        read_file(client, ADDRESS)
    assert "sha256 mismatch" in str(info.value) and ADDRESS in str(info.value)


def test_text_read_refuses_an_envelope_without_a_sha256():
    def handler(request):
        return httpx.Response(200, json=_envelope(TEXT, sha256=""))

    with _client(handler) as client, pytest.raises(IntegrityError):
        read_file(client, ADDRESS)


def test_a_base64_envelope_is_decoded_to_bytes_and_verified():
    encoded = base64.b64encode(PNG).decode("ascii")

    def handler(request):
        return httpx.Response(
            200, json=_envelope(encoded, encoding="base64", content_type="image/png"),
        )

    with _client(handler) as client:
        file = read_file(client, ADDRESS)

    assert not file.is_text and file.content == PNG and file.encoding == "base64"
    assert file.sha256 == _sha(PNG)


@pytest.mark.parametrize(
    "body",
    [
        {"content": None},
        {"content": "x", "encoding": "latin-1"},
        {"content": "not base64 !!", "encoding": "base64"},
    ],
)
def test_malformed_envelopes_are_refused(body):
    def handler(request):
        return httpx.Response(200, json={**_envelope(TEXT), **body})

    with _client(handler) as client, pytest.raises(BerilReadError):
        read_file(client, ADDRESS)


# --- read_file: bytes -------------------------------------------------------


def test_bytes_read_asks_for_octet_stream_and_verifies_the_header_sha256():
    seen = {}

    def handler(request):
        seen["accept"] = request.headers["Accept"]
        return _bytes_route(PNG)(request)

    with _client(handler) as client:
        file = read_file(client, "0009-0001-2345-6789/alpha/figures/fig1.png", as_bytes=True)

    assert seen["accept"] == "application/octet-stream"
    assert file.content == PNG and file.as_bytes() == PNG and not file.is_text
    assert file.encoding == "bytes" and file.size == len(PNG)
    assert file.sha256 == _sha(PNG) and file.source == "archive"
    assert file.content_type == "image/png" and file.path == "figures/fig1.png"


def test_bytes_read_fails_loudly_on_a_sha256_mismatch():
    with _client(_bytes_route(PNG, sha256=_sha(b"other"))) as client:
        with pytest.raises(IntegrityError) as info:
            read_file(client, ADDRESS, as_bytes=True)
    msg = str(info.value)
    assert "sha256 mismatch" in msg and _sha(b"other") in msg and _sha(PNG) in msg


def test_bytes_read_accepts_an_uppercase_header_digest():
    with _client(_bytes_route(PNG, sha256=_sha(PNG).upper())) as client:
        assert read_file(client, ADDRESS, as_bytes=True).sha256 == _sha(PNG)


def test_bytes_read_refuses_a_response_without_the_digest_header():
    def handler(request):
        return httpx.Response(200, content=PNG, headers={"Content-Type": "image/png"})

    with _client(handler) as client, pytest.raises(IntegrityError) as info:
        read_file(client, ADDRESS, as_bytes=True)
    assert "X-Content-SHA256" in str(info.value)


# --- read_file: errors ------------------------------------------------------


def test_a_403_names_the_allowlist():
    def handler(request):
        return httpx.Response(403, json={"detail": "path not readable"})

    with _client(handler) as client, pytest.raises(BerilReadError) as info:
        read_file(client, "0009-1/alpha/RESEARCH_PLAN.md")
    err = info.value
    assert err.status == 403
    assert "not readable" in str(err)
    for name in ("REPORT.md", "beril.yaml", "REFUTATION_<n>.md", "figures/**"):
        assert name in str(err)


def test_a_404_says_no_such_file():
    def handler(request):
        return httpx.Response(404, json={"detail": "not found"})

    with _client(handler) as client, pytest.raises(BerilReadError) as info:
        read_file(client, "0009-1/alpha/REPORT.md", as_bytes=True)
    assert info.value.status == 404
    assert "no such file: 0009-1/alpha/REPORT.md" in str(info.value)


def test_other_failures_carry_the_servers_detail_and_status():
    def handler(request):
        return httpx.Response(401, json={"detail": "bad token"})

    with _client(handler) as client, pytest.raises(BerilReadError) as info:
        read_file(client, ADDRESS)
    assert info.value.status == 401 and "bad token" in str(info.value)


def test_transport_errors_propagate_to_the_caller():
    def handler(request):
        raise httpx.ConnectError("down")

    with _client(handler) as client, pytest.raises(httpx.TransportError):
        read_file(client, ADDRESS)


# --- list_submissions -------------------------------------------------------


def _row(project: str, at: str, kind: str = "approved", files: int = 2) -> dict:
    return {
        "id": f"sub-{project}",
        "project": project,
        "owner_orcid": "0009-0001-2345-6789",
        "address": f"0009-0001-2345-6789/{project}",
        "revision": "cd" * 32,
        "submitted_at": at,
        "kind": kind,
        "archive_path": f"s3a://b/t/projects/{project}/",
        "files": [{"path": f"f{i}.md", "sha256": "ab" * 32, "size": 10} for i in range(files)],
    }


def test_submissions_sends_only_the_filters_given_and_parses_the_page():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json={
            "submissions": [_row("alpha", "2026-11-01T00:00:00Z"),
                            _row("beta", "2026-11-02T00:00:00Z", kind="seeded", files=0)],
            "next_since": "2026-11-02T00:00:00Z",
        })

    with _client(handler) as client:
        page = list_submissions(client)

    assert seen == {"path": SUBMISSIONS_PATH, "params": {}}
    assert [s.project for s in page.submissions] == ["alpha", "beta"]
    first = page.submissions[0]
    assert (first.id, first.owner_orcid, first.kind, first.revision, first.archive_path) == (
        "sub-alpha", "0009-0001-2345-6789", "approved", "cd" * 32, "s3a://b/t/projects/alpha/",
    )
    assert len(first.files) == 2
    assert first.files[0] == {"path": "f0.md", "sha256": "ab" * 32, "size": 10}
    assert page.submissions[1].files == []
    assert page.next_since == "2026-11-02T00:00:00Z"
    assert page.raw["next_since"] == "2026-11-02T00:00:00Z"


def test_submissions_pages_with_next_since():
    pages = {
        None: ([_row("a", "2026-11-01T00:00:00Z")], "2026-11-01T00:00:00Z"),
        "2026-11-01T00:00:00Z": ([_row("b", "2026-11-03T00:00:00Z")], "2026-11-03T00:00:00Z"),
        "2026-11-03T00:00:00Z": ([], None),
    }
    asked = []

    def handler(request):
        since = request.url.params.get("since")
        asked.append((since, request.url.params.get("kind"), request.url.params.get("limit")))
        rows, nxt = pages[since]
        return httpx.Response(200, json={"submissions": rows, "next_since": nxt})

    seen = []
    with _client(handler) as client:
        since = None
        while True:
            page = list_submissions(client, since=since, kinds=["approved", "seeded", "docs"], limit=1)
            seen += [s.project for s in page.submissions]
            if not page.submissions or page.next_since is None:
                break
            since = page.next_since

    assert seen == ["a", "b"]
    assert asked == [
        (None, "approved,seeded,docs", "1"),
        ("2026-11-01T00:00:00Z", "approved,seeded,docs", "1"),
        ("2026-11-03T00:00:00Z", "approved,seeded,docs", "1"),
    ]


def test_submissions_refuses_an_unknown_kind_before_any_request():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"submissions": []})

    with _client(handler) as client:
        with pytest.raises(ValueError, match="unknown submission kind.*rejected"):
            list_submissions(client, kinds=["approved", "rejected"])
        with pytest.raises(ValueError, match="--limit"):
            list_submissions(client, limit=0)
    assert calls == []


def test_submissions_without_a_next_since_is_the_last_page():
    def handler(request):
        return httpx.Response(200, json={"submissions": []})

    with _client(handler) as client:
        page = list_submissions(client, since="2026-11-03T00:00:00Z")
    assert page.submissions == [] and page.next_since is None


def test_submissions_surfaces_server_failures():
    def handler(request):
        return httpx.Response(500, json={"detail": "feed unavailable"})

    with _client(handler) as client, pytest.raises(BerilReadError) as info:
        list_submissions(client)
    assert info.value.status == 500 and "feed unavailable" in str(info.value)


def test_submissions_refuses_a_payload_without_the_list():
    def handler(request):
        return httpx.Response(200, json={"rows": []})

    with _client(handler) as client, pytest.raises(BerilReadError):
        list_submissions(client)


# --- source and revision ----------------------------------------------------


def test_read_sends_source_and_revision_only_when_given():
    seen = []

    def handler(request):
        seen.append(dict(request.url.params))
        return httpx.Response(200, json=_envelope(TEXT))

    with _client(handler) as client:
        read_file(client, ADDRESS)
        read_file(client, "wiki/concepts/carbon-yield", source="wiki")
        read_file(client, ADDRESS, revision="cd" * 32, as_bytes=False)

    assert seen == [
        {"address": ADDRESS},
        {"address": "wiki/concepts/carbon-yield", "source": "wiki"},
        {"address": ADDRESS, "revision": "cd" * 32},
    ]


def test_read_refuses_an_unknown_source_before_any_request():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=_envelope(TEXT))

    with _client(handler) as client, pytest.raises(ValueError, match="unknown source"):
        read_file(client, ADDRESS, source="github")
    assert calls == []
