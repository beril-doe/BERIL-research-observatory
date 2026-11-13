"""``POST /api/context/submissions``: the record ``/submit`` posts."""

from __future__ import annotations

import pytest

from app.db.models import Submission
from tests.submissions_helpers import (
    FILES,
    OWNER,
    REPORT,
    REVISION,
    TEXT_FILES,
    _login,
    manifest,
    post,
    sha,
)
from tests.test_routes_context import client, user  # noqa: F401  (fixtures)


def test_post_requires_a_login(client):
    assert post(client).status_code == 401


async def test_post_records_the_manifest_and_stores_the_bundle(client, user, db_session, submission_store):
    _login(client)

    resp = post(client)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert (body["created"], body["kind"], body["status"]) == (True, "approved", "pending")
    assert (body["project"], body["owner_orcid"], body["revision"]) == ("alpha", OWNER, REVISION)
    assert body["address"] == f"{OWNER}/alpha"
    assert body["approval_by"] == OWNER
    assert body["archive_path"].startswith("s3a://cdm-lake/")
    # Every archived file is on the manifest; only the bundled ones are stored.
    stored = {f["path"] for f in body["files"] if f["stored"]}
    assert stored == set(TEXT_FILES)
    assert {f["path"] for f in body["files"]} == set(FILES)
    # Only the figure the report embeds is still needed; fig2 is optional.
    assert body["missing"] == ["figures/fig1.png"]
    assert submission_store.get(OWNER, "alpha", REVISION, "REPORT.md") == REPORT
    row = await db_session.get(Submission, body["id"])
    assert (row.owner_user_id, row.status) == (user.id, "pending")


async def test_post_is_idempotent_on_owner_project_revision(client, user):
    _login(client)
    first = post(client).json()

    again = post(client)

    assert again.status_code == 200
    assert (again.json()["id"], again.json()["created"]) == (first["id"], False)


async def test_post_completes_at_once_when_no_figure_is_embedded(client, user):
    _login(client)
    report = b"# Alpha\n\nNo figures here.\n"
    files = {**FILES, "REPORT.md": report}
    body = manifest(revision=sha(report), report_hash=sha(report), files=files)

    resp = post(client, manifest_body=body, bundle={**{p: FILES[p] for p in TEXT_FILES}, "REPORT.md": report})

    assert resp.status_code == 200, resp.text
    assert (resp.json()["status"], resp.json()["missing"]) == ("complete", [])


@pytest.mark.parametrize(
    "change, code, needle",
    [
        ({"approver": "0000-0009-9999-9999"}, 403, "approved by someone else"),
        ({"owner": "0000-0009-9999-9999"}, 403, "owner_orcid"),
        ({"revision": "0" * 64}, 422, "revision"),
        ({"report_hash": "0" * 64}, 422, "report_hash"),
        ({"project": "My Project"}, 422, "slug"),
    ],
)
async def test_post_refuses_a_manifest_that_does_not_check_out(client, user, change, code, needle):
    _login(client)
    resp = post(client, manifest_body=manifest(**change))
    assert resp.status_code == code, resp.text
    assert needle in resp.json()["detail"]


async def test_post_refuses_a_bundled_file_that_does_not_match_the_manifest(client, user):
    _login(client)
    bundle = {p: FILES[p] for p in TEXT_FILES}
    bundle["README.md"] = b"# Tampered\n"

    resp = post(client, bundle=bundle)

    assert resp.status_code == 422
    assert "README.md" in resp.json()["detail"]


async def test_post_refuses_a_bundled_file_not_in_the_manifest(client, user):
    _login(client)
    resp = post(client, bundle={**{p: FILES[p] for p in TEXT_FILES}, "CORRECTIONS.md": b"x"})
    assert resp.status_code == 422
    assert "not in the manifest" in resp.json()["detail"]


async def test_post_refuses_figures_and_other_files_in_the_bundle(client, user):
    _login(client)
    resp = post(client, bundle={**{p: FILES[p] for p in TEXT_FILES}, "figures/fig1.png": FILES["figures/fig1.png"]})
    assert resp.status_code == 422
    assert "PUT" in resp.json()["detail"]


async def test_post_requires_report_in_the_bundle(client, user):
    _login(client)
    resp = post(client, bundle={"README.md": FILES["README.md"]})
    assert resp.status_code == 422
    assert "REPORT.md" in resp.json()["detail"]


async def test_post_rejects_a_manifest_without_report(client, user):
    _login(client)
    files = {p: c for p, c in FILES.items() if p != "REPORT.md"}
    resp = post(client, manifest_body=manifest(files=files))
    assert resp.status_code == 422
    assert "REPORT.md" in resp.json()["detail"]


async def test_post_rejects_a_traversing_manifest_path(client, user):
    _login(client)
    files = {**FILES, "../evil.md": b"x"}
    resp = post(client, manifest_body=manifest(files=files))
    assert resp.status_code == 422


async def test_post_rejects_malformed_json(client, user):
    _login(client)
    resp = client.post(
        "/api/context/submissions",
        files={"manifest": ("manifest.json", b"{nope", "application/json"),
               "bundle": ("bundle.zip", b"PK", "application/zip")},
    )
    assert resp.status_code == 400
