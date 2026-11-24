"""``POST /api/context/submissions``: the record ``/submit`` posts."""

from __future__ import annotations

import pytest

from app.context_manager.base import ContextFileNotFound
from app.db.models import Submission
from tests.submissions_helpers import (
    FILES,
    OWNER,
    REPORT,
    REVISION,
    TEXT_FILES,
    _login,
    beril_yaml,
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


async def test_repost_with_a_changed_file_is_refused_and_stores_nothing(client, user, submission_store):
    # The first post leaves README unstored; a retry under the same REPORT.md
    # revision carries a different README. Storing it would serve bytes the
    # feed's hash does not describe.
    _login(client)
    first = post(client, bundle={"REPORT.md": REPORT, "beril.yaml": FILES["beril.yaml"]}).json()
    changed = {**FILES, "README.md": b"# Alpha, edited\n"}

    again = post(
        client,
        manifest_body=manifest(files=changed),
        bundle={p: changed[p] for p in TEXT_FILES},
    )

    assert again.status_code == 409, again.text
    assert "README.md" in again.json()["detail"]
    status = client.get(f"/api/context/submissions/{first['id']}").json()
    assert {f["path"]: f["stored"] for f in status["files"]}["README.md"] is False
    with pytest.raises(ContextFileNotFound):
        submission_store.get(OWNER, "alpha", REVISION, "README.md")


async def test_repost_with_the_recorded_manifest_stores_what_was_missing(client, user, submission_store):
    _login(client)
    first = post(client, bundle={"REPORT.md": REPORT, "beril.yaml": FILES["beril.yaml"]}).json()

    again = post(client)

    assert again.status_code == 200, again.text
    assert again.json()["id"] == first["id"]
    assert submission_store.get(OWNER, "alpha", REVISION, "README.md") == FILES["README.md"]


async def test_post_completes_at_once_when_no_figure_is_embedded(client, user):
    _login(client)
    report = b"# Alpha\n\nNo figures here.\n"
    files = {**FILES, "REPORT.md": report, "beril.yaml": beril_yaml(report=report)}
    body = manifest(revision=sha(report), report_hash=sha(report), files=files)

    resp = post(client, manifest_body=body, bundle={p: files[p] for p in TEXT_FILES})

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


def test_file_sizes_are_stored_as_64_bit():
    """The manifest lists every archived file, datasets included; a 32-bit
    column cannot hold a size past 2 GiB on Postgres."""
    from sqlalchemy import BigInteger

    from app.db.models import SubmissionFile

    assert isinstance(SubmissionFile.__table__.c.size.type, BigInteger)


@pytest.mark.parametrize("size, code", [(3 * 2**30, 200), (2**63, 422)])
async def test_post_takes_a_large_archived_file_and_refuses_one_past_bigint(client, user, size, code):
    _login(client)
    body = manifest()
    body["files"].append({"path": "data/big.parquet", "sha256": "ab" * 32, "size": size})

    resp = post(client, manifest_body=body)

    assert resp.status_code == code, resp.text


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
    resp = post(client, bundle={"README.md": FILES["README.md"], "beril.yaml": FILES["beril.yaml"]})
    assert resp.status_code == 422
    assert "REPORT.md" in resp.json()["detail"]


@pytest.mark.parametrize(
    "bundle_yaml, code, needle",
    [
        (None, 422, "must carry beril.yaml"),
        (beril_yaml(status="in_review"), 422, "not approved"),
        (beril_yaml(approver="0000-0009-9999-9999"), 403, "approved by someone else"),
        (beril_yaml(project="beta"), 422, "names project"),
        (beril_yaml(report=b"# An earlier report\n"), 422, "REPORT.md does not match"),
        (beril_yaml(review=b"# A different review\n"), 422, "REVIEW.md does not match"),
        (b"project_id: alpha\nstatus: complete\n", 422, "no approval block"),
        (b"- not\n- a mapping\n", 422, "not a mapping"),
    ],
)
async def test_post_refuses_a_submission_its_beril_yaml_does_not_approve(
    client, user, db_session, submission_store, bundle_yaml, code, needle
):
    """The ingest gate's approval rule: without a beril.yaml approving this
    REPORT.md and REVIEW.md by the caller, nothing is recorded."""
    _login(client)
    files = dict(FILES) if bundle_yaml is None else {**FILES, "beril.yaml": bundle_yaml}
    files = {p: c for p, c in files.items() if not (bundle_yaml is None and p == "beril.yaml")}
    bundle = {p: files[p] for p in TEXT_FILES if p in files}

    resp = post(client, manifest_body=manifest(files=files), bundle=bundle)

    assert resp.status_code == code, resp.text
    assert needle in resp.json()["detail"]
    from sqlalchemy import func, select

    assert (await db_session.execute(select(func.count()).select_from(Submission))).scalar_one() == 0
    assert not submission_store.exists(OWNER, "alpha", REVISION, "REPORT.md")



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
