"""``GET /api/context/submissions``: the feed of complete submissions."""

from __future__ import annotations

from datetime import timedelta

import pytest

from tests.submissions_helpers import (
    FIG1,
    FILES,
    OWNER,
    SUBMITTED_AT,
    _login,
    post,
    put_file,
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


async def test_feed_lists_complete_submissions_in_completion_order(client, user):
    _login(client)
    later = submit_complete(client, report=b"# v2\n", submitted_at=SUBMITTED_AT + timedelta(days=1))
    first = submit_complete(client, report=b"# v1\n", submitted_at=SUBMITTED_AT)

    resp = _feed(client)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    # Completion order, not submitted_at: v2 completed first.
    assert [s["id"] for s in body["submissions"]] == [later, first]
    entry = body["submissions"][0]
    assert (entry["project"], entry["owner_orcid"], entry["kind"]) == ("alpha", OWNER, "approved")
    assert entry["address"] == f"{OWNER}/alpha"
    assert entry["revision"] == sha(b"# v2\n")
    assert entry["submitted_at"] == (SUBMITTED_AT + timedelta(days=1)).isoformat()
    assert entry["archive_path"].startswith("s3a://")
    # Only stored files are listed, each with the hash /read serves byte-exact.
    assert {f["path"] for f in entry["files"]} == {"REPORT.md", "README.md", "beril.yaml"}
    assert {f["path"]: (f["sha256"], f["size"]) for f in entry["files"]}["README.md"] == (
        sha(FILES["README.md"]), len(FILES["README.md"])
    )
    assert isinstance(body["next_after"], int)
    assert "next_since" not in body
    assert "stored" not in entry["files"][0]


async def test_feed_omits_pending_submissions(client, user):
    _login(client)
    pending = post(client).json()  # fig1 not yet PUT
    assert pending["status"] == "pending"

    assert _feed(client).json()["submissions"] == []


async def test_feed_after_is_exclusive_and_pages_by_next_after(client, user):
    _login(client)
    ids = [
        submit_complete(client, report=f"# v{d}\n".encode(), submitted_at=SUBMITTED_AT + timedelta(days=d))
        for d in range(3)
    ]

    page = _feed(client, limit=2).json()
    assert [s["id"] for s in page["submissions"]] == ids[:2]

    rest = _feed(client, after=page["next_after"]).json()
    assert [s["id"] for s in rest["submissions"]] == ids[2:]

    empty = _feed(client, after=rest["next_after"]).json()
    assert (empty["submissions"], empty["next_after"]) == ([], rest["next_after"])


async def test_a_submission_completing_after_a_later_one_was_fed_is_not_skipped(client, user):
    # A is posted first but its figure arrives last; B completes in between
    # and is fed. A must still come after the cursor B's page handed out.
    _login(client)
    a = post(client).json()  # embeds fig1, not yet PUT
    assert a["status"] == "pending"
    b = submit_complete(client, report=b"# beta\n", submitted_at=SUBMITTED_AT + timedelta(days=1))
    page = _feed(client).json()
    assert [s["id"] for s in page["submissions"]] == [b]

    assert put_file(client, a["id"], "figures/fig1.png", FIG1).json()["status"] == "complete"

    nxt = _feed(client, after=page["next_after"]).json()
    assert [s["id"] for s in nxt["submissions"]] == [a["id"]]


async def test_submissions_sharing_a_timestamp_all_page_through_one_at_a_time(client, user):
    _login(client)
    ids = {
        submit_complete(client, report=f"# same time {n}\n".encode(), submitted_at=SUBMITTED_AT)
        for n in range(3)
    }

    seen, after = [], None
    for _ in range(5):
        params = {"limit": 1} if after is None else {"limit": 1, "after": after}
        body = _feed(client, **params).json()
        if not body["submissions"]:
            break
        seen += [s["id"] for s in body["submissions"]]
        after = body["next_after"]

    assert sorted(seen) == sorted(ids)


async def test_feed_since_still_pages_by_next_since(client, user):
    # The deprecated cursor, kept for clients not yet on `after`.
    _login(client)
    ids = [
        submit_complete(client, report=f"# v{d}\n".encode(), submitted_at=SUBMITTED_AT + timedelta(days=d))
        for d in range(3)
    ]

    page = _feed(client, since="2026-01-01T00:00:00Z", limit=2).json()
    assert [s["id"] for s in page["submissions"]] == ids[:2]
    assert "next_after" not in page

    rest = _feed(client, since=page["next_since"]).json()
    assert [s["id"] for s in rest["submissions"]] == ids[2:]

    empty = _feed(client, since=rest["next_since"]).json()
    assert (empty["submissions"], empty["next_since"]) == ([], rest["next_since"])


async def test_feed_refuses_both_cursors_and_a_negative_after(client, user):
    _login(client)
    assert _feed(client, after=1, since="2026-11-10T00:00:00Z").status_code == 422
    assert _feed(client, after=-1).status_code == 422


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


@pytest.mark.parametrize(
    "kind, review_stored, status, missing",
    [
        ("approved", True, "complete", []),
        # However it was recorded, an approved submission without its stored
        # review is never complete, so never in the feed.
        ("approved", False, "pending", ["REVIEW.md"]),
        ("approved", None, "pending", ["REVIEW.md"]),  # not even listed
        ("seeded", None, "complete", []),  # predates /submit: no review asked
    ],
)
def test_an_approved_submission_is_complete_only_with_its_review(kind, review_stored, status, missing):
    from app.db.models import Submission, SubmissionFile
    from app.submissions.service import compute_status, missing_paths

    files = [SubmissionFile(path="REPORT.md", sha256="a" * 64, size=1, stored=True)]
    if review_stored is not None:
        files.append(SubmissionFile(path="REVIEW.md", sha256="b" * 64, size=1, stored=review_stored))
    submission = Submission(kind=kind, files=files)

    assert compute_status(submission, "# R\n") == status
    assert missing_paths(submission, "# R\n") == missing
