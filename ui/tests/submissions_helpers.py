"""Shared helpers for the submission-record tests (not a test module)."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone

from tests.test_routes_context import USER_TOKEN, _login  # noqa: F401  (re-exported)

OWNER = USER_TOKEN["orcid"]
REPORT = b"# Alpha\n\n![Fig 1](figures/fig1.png)\n\nExact bytes.\n"
README = b"# Alpha\n"
REVIEW = b"# Review\n\nApproved.\n"


def beril_yaml(*, project="alpha", report=REPORT, review=REVIEW, approver=OWNER, status="complete") -> bytes:
    """The ``beril.yaml`` /submit writes: an approval by ``approver`` of
    exactly these REPORT.md and REVIEW.md bytes."""
    return (
        f"project_id: {project}\nstatus: {status}\napproval:\n  by: '{approver}'\n"
        f"  at: '2026-11-10T11:00:00Z'\n"
        f"  report_hash: sha256:{hashlib.sha256(report).hexdigest()}\n"
        f"  review_hash: sha256:{hashlib.sha256(review).hexdigest()}\n"
    ).encode()


BERIL_YAML = beril_yaml()
FIG1 = b"\x89PNG\r\n\x1a\n\x00fig1"
FIG2 = b"\x89PNG\r\n\x1a\n\x00fig2"
SUBMITTED_AT = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)

# What the archive step uploads for the alpha project: text files, the
# review (archived, not bundled), two figures (one embedded, one not), and a
# data file the wiki never reads.
FILES = {
    "REPORT.md": REPORT,
    "README.md": README,
    "beril.yaml": BERIL_YAML,
    "REVIEW.md": REVIEW,
    "figures/fig1.png": FIG1,
    "figures/fig2.png": FIG2,
    "data/table.csv": b"a,b\n1,2\n",
}
TEXT_FILES = ("REPORT.md", "README.md", "beril.yaml")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


REVISION = sha(REPORT)


def zip_bytes(members: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return buf.getvalue()


def manifest(
    *,
    project="alpha",
    owner=OWNER,
    revision=REVISION,
    files=FILES,
    approver=OWNER,
    report_hash=REVISION,
    submitted_at=SUBMITTED_AT,
    archive_path="s3a://cdm-lake/tenant-general-warehouse/microbialdiscoveryforge/projects/alpha",
    **extra,
) -> dict:
    body = {
        "project": project,
        "owner_orcid": owner,
        "revision": revision,
        "submitted_at": submitted_at.isoformat(),
        "archive_path": archive_path,
        "approval": {"by": approver, "at": "2026-11-10T11:00:00Z", "report_hash": report_hash},
        "files": [{"path": p, "sha256": sha(c), "size": len(c)} for p, c in files.items()],
    }
    body.update(extra)
    return body


def post(client, *, manifest_body=None, bundle=None):
    manifest_body = manifest() if manifest_body is None else manifest_body
    bundle = {p: FILES[p] for p in TEXT_FILES} if bundle is None else bundle
    return client.post(
        "/api/context/submissions",
        files={
            "manifest": ("manifest.json", json.dumps(manifest_body).encode(), "application/json"),
            "bundle": ("bundle.zip", zip_bytes(bundle), "application/zip"),
        },
    )


def put_file(client, submission_id, path, data: bytes):
    return client.put(
        f"/api/context/submissions/{submission_id}/files/{path}",
        content=data,
        headers={"Content-Type": "application/octet-stream"},
    )


def submit_complete(client, *, project="alpha", report=REPORT, files=None, submitted_at=SUBMITTED_AT):
    """Post a submission and PUT its embedded figure, returning its id."""
    files = dict(FILES, REPORT=report) if files is None else files
    files = {k: v for k, v in files.items() if k != "REPORT"}
    files["REPORT.md"] = report
    files["beril.yaml"] = beril_yaml(project=project, report=report, review=files.get("REVIEW.md", REVIEW))
    body = manifest(project=project, revision=sha(report), report_hash=sha(report), files=files,
                    submitted_at=submitted_at)
    resp = post(client, manifest_body=body, bundle={p: files[p] for p in TEXT_FILES if p in files})
    assert resp.status_code == 200, resp.text
    sid = resp.json()["id"]
    for path in resp.json()["missing"]:
        assert put_file(client, sid, path, files[path]).status_code == 200
    return sid
