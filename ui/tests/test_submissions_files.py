"""``PUT /api/context/submissions/{id}/files/{path}`` and the status route."""

from __future__ import annotations

from app.db.models import BerilUser
from tests.submissions_helpers import (
    FIG1,
    FIG2,
    OWNER,
    REVISION,
    _login,
    post,
    put_file,
)
from tests.test_routes_context import client, user  # noqa: F401  (fixtures)


def _posted(client):
    _login(client)
    body = post(client).json()
    return body["id"]


async def test_put_stores_a_figure_and_completes_the_submission(client, user, submission_store):
    sid = _posted(client)

    resp = put_file(client, sid, "figures/fig1.png", FIG1)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert (body["path"], body["stored"], body["status"], body["missing"]) == (
        "figures/fig1.png", True, "complete", []
    )
    assert submission_store.get(OWNER, "alpha", REVISION, "figures/fig1.png") == FIG1


async def test_put_of_an_unembedded_figure_is_stored_but_was_never_required(client, user):
    sid = _posted(client)

    resp = put_file(client, sid, "figures/fig2.png", FIG2)

    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"  # fig1 still missing
    assert resp.json()["missing"] == ["figures/fig1.png"]
    status = client.get(f"/api/context/submissions/{sid}").json()
    assert {f["path"] for f in status["files"] if f["stored"]} >= {"figures/fig2.png", "REPORT.md"}


async def test_put_refuses_bytes_that_do_not_hash_to_the_manifest(client, user, submission_store):
    sid = _posted(client)

    resp = put_file(client, sid, "figures/fig1.png", b"not the figure")

    assert resp.status_code == 422
    assert "sha256" in resp.json()["detail"]
    assert not submission_store.exists(OWNER, "alpha", REVISION, "figures/fig1.png")


async def test_put_is_a_noop_once_stored(client, user):
    sid = _posted(client)
    assert put_file(client, sid, "figures/fig1.png", FIG1).status_code == 200
    # Different bytes after the fact are ignored: the stored copy stands.
    resp = put_file(client, sid, "figures/fig1.png", b"other")
    assert resp.status_code == 200
    assert resp.json()["stored"] is True


async def test_put_of_a_path_not_in_the_manifest_is_404(client, user):
    sid = _posted(client)
    assert put_file(client, sid, "figures/nope.png", FIG1).status_code == 404


async def test_put_of_a_non_wiki_file_is_403(client, user):
    """data/ is on the manifest (every archived file is) but BERIL does not
    hold it."""
    sid = _posted(client)
    resp = put_file(client, sid, "data/table.csv", b"a,b\n1,2\n")
    assert resp.status_code == 403


async def test_put_by_someone_else_is_404(client, user, db_session):
    sid = _posted(client)
    other = BerilUser(orcid_id="0000-0009-9999-9999", display_name="Other")
    db_session.add(other)
    await db_session.commit()
    _login(client, {"access_token": "t", "token_type": "bearer", "orcid": "0000-0009-9999-9999", "name": "Other"})

    assert put_file(client, sid, "figures/fig1.png", FIG1).status_code == 404


async def test_put_of_an_unknown_submission_is_404(client, user):
    _login(client)
    assert put_file(client, "nope", "figures/fig1.png", FIG1).status_code == 404


async def test_put_refuses_a_file_over_the_limit(client, user, monkeypatch):
    from app.config import get_settings

    sid = _posted(client)
    monkeypatch.setattr(get_settings(), "submissions_max_file_bytes", 4)
    assert put_file(client, sid, "figures/fig1.png", FIG1).status_code == 413


def test_put_requires_a_login(client):
    assert put_file(client, "x", "figures/fig1.png", FIG1).status_code == 401


async def test_status_reports_stored_flags_and_missing(client, user):
    sid = _posted(client)
    resp = client.get(f"/api/context/submissions/{sid}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["missing"] == ["figures/fig1.png"]
    assert {f["path"]: f["stored"] for f in body["files"]}["data/table.csv"] is False


async def test_status_of_an_unknown_submission_is_404(client, user):
    _login(client)
    assert client.get("/api/context/submissions/nope").status_code == 404
