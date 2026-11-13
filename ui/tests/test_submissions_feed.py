"""``GET /api/context/submissions``: the feed of complete submissions."""

from __future__ import annotations

from datetime import timedelta

from tests.submissions_helpers import (
    FILES,
    OWNER,
    SUBMITTED_AT,
    _login,
    post,
    sha,
    submit_complete,
)
from tests.test_routes_context import (  # noqa: F401  (fixtures)
    _OWNER_ORCID,
    _import,
    _make_admin,
    _repo_project,
    admin_store,
    client,
    credentialed_user,
    user,
)


def _feed(client, **params):
    return client.get("/api/context/submissions", params=params)


def test_feed_requires_a_login(client):
    assert _feed(client).status_code == 401


async def test_feed_lists_complete_submissions_oldest_first(client, user):
    _login(client)
    later = submit_complete(client, report=b"# v2\n", submitted_at=SUBMITTED_AT + timedelta(days=1))
    first = submit_complete(client, report=b"# v1\n", submitted_at=SUBMITTED_AT)

    resp = _feed(client)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert [s["id"] for s in body["submissions"]] == [first, later]
    entry = body["submissions"][1]
    assert (entry["project"], entry["owner_orcid"], entry["kind"]) == ("alpha", OWNER, "approved")
    assert entry["address"] == f"{OWNER}/alpha"
    assert entry["revision"] == sha(b"# v2\n")
    assert entry["archive_path"].startswith("s3a://")
    # Only stored files are listed, each with the hash /read serves byte-exact.
    assert {f["path"] for f in entry["files"]} == {"REPORT.md", "README.md", "beril.yaml"}
    assert {f["path"]: (f["sha256"], f["size"]) for f in entry["files"]}["README.md"] == (
        sha(FILES["README.md"]), len(FILES["README.md"])
    )
    assert body["next_since"] == entry["submitted_at"]
    assert "stored" not in entry["files"][0]


async def test_feed_omits_pending_submissions(client, user):
    _login(client)
    pending = post(client).json()  # fig1 not yet PUT
    assert pending["status"] == "pending"

    assert _feed(client).json()["submissions"] == []


async def test_feed_since_is_exclusive_and_pages_by_next_since(client, user):
    _login(client)
    ids = [
        submit_complete(client, report=f"# v{d}\n".encode(), submitted_at=SUBMITTED_AT + timedelta(days=d))
        for d in range(3)
    ]

    page = _feed(client, limit=2).json()
    assert [s["id"] for s in page["submissions"]] == ids[:2]

    rest = _feed(client, since=page["next_since"]).json()
    assert [s["id"] for s in rest["submissions"]] == ids[2:]

    empty = _feed(client, since=rest["next_since"]).json()
    assert (empty["submissions"], empty["next_since"]) == ([], rest["next_since"])


async def test_feed_accepts_zulu_and_date_since_and_refuses_junk(client, user):
    _login(client)
    submit_complete(client, report=b"# v\n")

    assert len(_feed(client, since="2026-11-10T00:00:00Z").json()["submissions"]) == 1
    assert len(_feed(client, since="2026-11-11").json()["submissions"]) == 0
    assert _feed(client, since="yesterday").status_code == 422


async def test_feed_filters_by_kind(client, user):
    _login(client)
    approved = submit_complete(client, report=b"# v\n")

    assert [s["id"] for s in _feed(client, kind="approved").json()["submissions"]] == [approved]
    assert _feed(client, kind="seeded").json()["submissions"] == []
    assert _feed(client, kind="approved, seeded").status_code == 200
    assert _feed(client, kind="retirement").status_code == 422
    assert _feed(client, kind="").status_code == 422


async def test_an_admin_import_lands_on_the_feed_as_seeded(client, credentialed_user, db_session, admin_store):
    """The import records a seeded submission under the project's repo
    owner; it is complete at once (an import carries no figures)."""
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = _import(client, members={"REPORT.md": b"# Report\n", "README.md": b"# Readme\n"})

    assert resp.status_code == 200, resp.text
    sid = resp.json()["submission_id"]
    assert sid
    feed = _feed(client, kind="seeded").json()["submissions"]
    assert [(s["id"], s["kind"], s["owner_orcid"], s["address"]) for s in feed] == [
        (sid, "seeded", _OWNER_ORCID, f"{_OWNER_ORCID}/alpha_proj")
    ]
    assert {f["path"]: f["sha256"] for f in feed[0]["files"]} == {
        "REPORT.md": sha(b"# Report\n"), "README.md": sha(b"# Readme\n")
    }
    # Re-importing the same report is idempotent.
    again = _import(client, members={"REPORT.md": b"# Report\n", "README.md": b"# Readme\n"})
    assert again.json()["submission_id"] == sid
    assert len(_feed(client, kind="seeded").json()["submissions"]) == 1


async def test_an_import_without_a_report_records_no_submission(
    client, credentialed_user, db_session, admin_store
):
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)
    resp = _import(client, members={"README.md": b"# Readme\n"})
    assert resp.status_code == 200
    assert resp.json()["submission_id"] is None
