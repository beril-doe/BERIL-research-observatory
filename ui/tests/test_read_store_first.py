"""``GET /api/context/read`` consults the submission store before the
context store / archive chain, and ``import_docs`` feeds the digests."""

from __future__ import annotations

import base64
import io
import zipfile

from tests.submissions_helpers import (
    FIG1,
    FILES,
    OWNER,
    REPORT,
    REVISION,
    _login,
    sha,
    submit_complete,
)
from tests.test_routes_context import (  # noqa: F401  (fixtures)
    _make_admin,
    client,
    credentialed_user,
    read_manager,
    user,
)


def _read(client, address, **params):
    return client.get("/api/context/read", params={"address": address, **params})


async def test_read_serves_the_submission_store_byte_exact(client, user, read_manager):
    _login(client)
    sid = submit_complete(client)

    resp = _read(client, f"{OWNER}/alpha/REPORT.md")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert (body["source"], body["revision"], body["sha256"]) == ("submission", REVISION, sha(REPORT))
    assert body["content"] == REPORT.decode()
    assert body["modified_at"] in ("2026-11-10T12:00:00+00:00", "2026-11-10T12:00:00Z")
    # No project row, no context store: the submission alone made it readable.
    read_manager.get_file.assert_not_awaited()
    assert sid


async def test_read_serves_a_stored_figure_as_base64(client, user, read_manager):
    _login(client)
    submit_complete(client)

    resp = _read(client, f"{OWNER}/alpha/figures/fig1.png")

    body = resp.json()
    assert (body["source"], body["encoding"], body["content_type"]) == ("submission", "base64", "image/png")
    assert base64.b64decode(body["content"]) == FIG1


async def test_read_as_octet_stream_carries_the_revision_header(client, user, read_manager):
    _login(client)
    submit_complete(client)

    resp = client.get("/api/context/read", params={"address": f"{OWNER}/alpha/REPORT.md"},
                      headers={"Accept": "application/octet-stream"})

    assert resp.content == REPORT
    assert resp.headers["x-content-source"] == "submission"
    assert resp.headers["x-content-revision"] == REVISION
    assert resp.headers["x-content-modified-at"] == "2026-11-10T12:00:00+00:00"


async def test_read_picks_the_newest_complete_revision_unless_one_is_named(client, user, read_manager):
    _login(client)
    from datetime import timedelta

    from tests.submissions_helpers import SUBMITTED_AT

    old = b"# v1\n\n![f](figures/fig1.png)\n"
    new = b"# v2\n\n![f](figures/fig1.png)\n"
    submit_complete(client, report=old, submitted_at=SUBMITTED_AT)
    submit_complete(client, report=new, submitted_at=SUBMITTED_AT + timedelta(days=1))

    assert _read(client, f"{OWNER}/alpha/REPORT.md").json()["content"] == new.decode()
    assert _read(client, f"{OWNER}/alpha/REPORT.md", revision=sha(old)).json()["content"] == old.decode()
    assert _read(client, f"{OWNER}/alpha/REPORT.md", revision="0" * 64).status_code == 404
    assert _read(client, f"{OWNER}/alpha/REPORT.md", revision="nope").status_code == 422


async def test_read_falls_back_to_the_legacy_chain_without_a_submission(
    client, credentialed_user, db_session, read_manager
):
    """A project ingested before submission records exist still reads through
    the context store / archive chain."""
    from tests.test_routes_context import _own_project

    await _own_project(db_session, credentialed_user)
    _login(client)

    resp = _read(client, f"{OWNER}/alpha/REPORT.md")

    assert resp.status_code == 200
    assert resp.json()["source"] == "context"
    read_manager.get_file.assert_awaited_once()


async def test_read_of_a_pending_submission_falls_back_too(client, credentialed_user, db_session, read_manager):
    """Only a complete submission answers; a half-landed one must not serve
    a report whose figures are missing."""
    from tests.submissions_helpers import post
    from tests.test_routes_context import _own_project

    await _own_project(db_session, credentialed_user)
    _login(client)
    post(client)  # fig1 never PUT

    assert _read(client, f"{OWNER}/alpha/REPORT.md").json()["source"] == "context"


async def test_import_docs_records_the_digests_as_kind_docs(client, credentialed_user, db_session, read_manager):
    await _make_admin(db_session, credentialed_user)
    _login(client)
    members = {"discoveries.md": b"# Discoveries\n", "pitfalls.md": b"# Pitfalls\n"}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)

    resp = client.post(
        "/api/admin/context/import_docs",
        files={"archive": ("docs.zip", buf.getvalue(), "application/zip"),
               "manifest": ("manifest.txt", "\n".join(members).encode(), "text/plain")},
    )

    assert resp.status_code == 200, resp.text
    assert (resp.json()["status"], resp.json()["created"]) == ("complete", True)
    feed = client.get("/api/context/submissions", params={"kind": "docs"}).json()["submissions"]
    assert [(s["owner_orcid"], s["project"], s["kind"]) for s in feed] == [("beril", "docs", "docs")]
    assert client.get("/api/context/submissions").json()["submissions"] == []  # default kinds exclude docs
    read = _read(client, "beril/docs/discoveries.md")
    assert (read.status_code, read.json()["content"]) == (200, "# Discoveries\n")
    assert _read(client, "beril/docs/REPORT.md").status_code == 404


async def test_import_docs_refuses_other_files_and_non_admins(client, credentialed_user, db_session):
    _login(client)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("REPORT.md", b"x")
    files = {"archive": ("docs.zip", buf.getvalue(), "application/zip"),
             "manifest": ("manifest.txt", b"REPORT.md", "text/plain")}
    assert client.post("/api/admin/context/import_docs", files=files).status_code == 403
    await _make_admin(db_session, credentialed_user)
    assert client.post("/api/admin/context/import_docs", files=files).status_code == 422
