"""Tests for the context-manager routes (``/api/context/*``).

These exercise the route layer only: auth, credential lookup, decryption of the
stored per-user key, and request/response shaping. ``OpenVikingManager`` is
patched out, so no OpenViking instance is needed. The end-to-end mapping from an
OV payload to ``ContextQueryResults`` is covered in ``test_context_manager.py``.
"""

from __future__ import annotations

import hashlib
import io
import os
import zipfile
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from openviking_sdk.errors import UnavailableError

from app.clients.openviking import OpenVikingError
from app.config import get_settings
from app.context_manager.base import (
    ContextIngestResults,
    ContextQueryResults,
    IngestResult,
    QueryResult,
)
from app.crypto import encrypt_secret
from app.db.crud import (
    create_user_project,
    get_ingest_batch,
    get_project_by_slug,
    get_projects_for_user,
)
from app.db.models import BerilUser, OvUserCredential
from app.db.session import get_db
from app.main import create_app

_CREDENTIAL_KEY = Fernet.generate_key().decode()

_ENV = {
    "BERIL_TEST_SKIP_LIFESPAN": "True",
    "BERIL_ORCID_CLIENT_ID": "APP-TESTCLIENTID",
    "BERIL_ORCID_CLIENT_SECRET": "test-secret",
    "BERIL_ORCID_BASE_URL": "https://sandbox.orcid.org",
    "BERIL_SESSION_SECRET_KEY": "test-session-secret",
    "BERIL_OV_URL": "http://ov.test:1933",
    "BERIL_OV_ACCOUNT_ID": "beril",
    "BERIL_OV_ADMIN_KEY": "admin-key",
    "BERIL_OV_CREDENTIAL_KEY": _CREDENTIAL_KEY,
}

USER_TOKEN = {
    "access_token": "fake-access-token",
    "token_type": "bearer",
    "orcid": "0000-0001-2345-6789",
    "name": "Alice Researcher",
}

QUERY_RESULTS = ContextQueryResults(
    query="alpha",
    results=[
        QueryResult(
            uri="viking://resources/projects/alpha.md",
            context_type="document",
            score=0.93,
            text="Alpha project overview.",
        )
    ],
)


def _make_mock_oauth_client(token: dict):
    auth_url = "https://sandbox.orcid.org/oauth/authorize?client_id=APP-TESTCLIENTID"
    mock_instance = MagicMock()
    mock_instance.create_authorization_url = MagicMock(return_value=(auth_url, "mock-state"))
    mock_instance.fetch_token = AsyncMock(return_value=token)
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    return MagicMock(return_value=mock_instance)


def _login(client: TestClient, token: dict = USER_TOKEN) -> None:
    mock_class = _make_mock_oauth_client(token)
    with patch("app.routes.auth.AsyncOAuth2Client", mock_class):
        client.get("/auth/orcid/callback", params={"code": "fake-code"}, follow_redirects=False)


@pytest.fixture
def client(repository_data, app_data_context, db_session):
    with patch.dict(os.environ, _ENV):
        import app.config as cfg

        cfg._settings = None
        app_instance = create_app()

        async def override_get_db() -> AsyncGenerator:
            yield db_session

        app_instance.dependency_overrides[get_db] = override_get_db
        with TestClient(app_instance, raise_server_exceptions=True) as c:
            app_instance.state.repo_data = repository_data
            app_instance.state.base_context = app_data_context
            yield c
        cfg._settings = None


@pytest.fixture
async def user(db_session):
    u = BerilUser(orcid_id=USER_TOKEN["orcid"], display_name=USER_TOKEN["name"])
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


@pytest.fixture
async def credentialed_user(db_session, user):
    """A user with a stored, Fernet-encrypted OpenViking key."""
    db_session.add(
        OvUserCredential(
            user_id=user.id,
            account_id="beril",
            ov_user_id=user.orcid_id,
            encrypted_key=encrypt_secret("plain-user-key", _CREDENTIAL_KEY),
        )
    )
    await db_session.commit()
    return user


@pytest.fixture
def manager():
    """Patch OpenVikingManager in the routes module; yields the instance."""
    inst = MagicMock()
    inst.query = AsyncMock(return_value=QUERY_RESULTS)
    inst.list_files = AsyncMock(return_value=["alpha.md", "beta.md"])
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_find_unauthenticated_returns_401(client):
    resp = client.post("/api/context/find", json={"query": "alpha"})
    assert resp.status_code == 401


def test_ls_unauthenticated_returns_401(client):
    assert client.get("/api/context/ls").status_code == 401


# ---------------------------------------------------------------------------
# POST /api/context/find
# ---------------------------------------------------------------------------


async def test_find_returns_mapped_results(client, credentialed_user, manager):
    _login(client)
    resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "alpha"
    assert body["results"] == [
        {
            "uri": "viking://resources/projects/alpha.md",
            "context_type": "document",
            "score": 0.93,
            "text": "Alpha project overview.",
            # Absent from this fixture's hit, so they serialize as null rather
            # than being omitted — clients can index them unconditionally.
            "match_reason": None,
            "content": None,
        }
    ]


async def test_find_forwards_body_to_manager(client, credentialed_user, manager):
    _login(client)
    resp = client.post(
        "/api/context/find",
        json={
            "query": "alpha",
            "root_path": "viking://resources/projects",
            "limit": 3,
            "score_threshold": 0.5,
        },
    )

    assert resp.status_code == 200
    sent = manager.query.await_args.args[0]
    assert sent.query == "alpha"
    assert sent.root_path == "viking://resources/projects"
    assert sent.limit == 3
    assert sent.score_threshold == 0.5


async def test_find_applies_query_defaults(client, credentialed_user, manager):
    """Only ``query`` is required; the rest come from ContextQuery defaults."""
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})

    sent = manager.query.await_args.args[0]
    assert sent.root_path is None
    assert sent.limit == 10
    assert sent.score_threshold is None


async def test_find_decrypts_stored_key_for_manager(client, credentialed_user):
    """The manager is constructed with the decrypted key, not the ciphertext."""
    _login(client)
    inst = MagicMock()
    inst.query = AsyncMock(return_value=QUERY_RESULTS)
    with patch("app.routes.context.OpenVikingManager", return_value=inst) as cls:
        client.post("/api/context/find", json={"query": "alpha"})

    assert cls.call_args.args[1] == "plain-user-key"


async def test_find_rejects_missing_query_field(client, credentialed_user, manager):
    _login(client)
    resp = client.post("/api/context/find", json={})

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_rejects_malformed_limit(client, credentialed_user, manager):
    _login(client)
    resp = client.post("/api/context/find", json={"query": "a", "limit": "lots"})

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_forwards_the_extended_options(client, credentialed_user, manager):
    _login(client)
    resp = client.post(
        "/api/context/find",
        json={
            "query": "alpha",
            "filter": {"op": "must", "field": "uri", "conds": ["viking://x/"]},
            "since": "7d",
            "until": "2026-01-01",
            "time_field": "created_at",
            "node_limit": 50,
            "read_content": True,
        },
    )

    assert resp.status_code == 200
    sent = manager.query.await_args.args[0]
    assert sent.filter == {"op": "must", "field": "uri", "conds": ["viking://x/"]}
    assert (sent.since, sent.until, sent.time_field) == ("7d", "2026-01-01", "created_at")
    assert sent.node_limit == 50
    assert sent.read_content is True


async def test_find_applies_extended_defaults(client, credentialed_user, manager):
    """The new options are all opt-in; none changes behavior when omitted."""
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})

    sent = manager.query.await_args.args[0]
    assert sent.filter is None
    assert (sent.since, sent.until, sent.time_field) == (None, None, None)
    assert sent.node_limit is None
    assert sent.read_content is False


@pytest.mark.parametrize(
    "payload",
    [
        {"query": "a", "limit": 0},
        {"query": "a", "limit": 100000},
        {"query": "a", "node_limit": 0},
        {"query": "a", "node_limit": 10_000_000},
    ],
)
async def test_find_rejects_out_of_range_limits(
    client, credentialed_user, manager, payload
):
    """An absurd limit is refused rather than forwarded to the backend."""
    _login(client)
    resp = client.post("/api/context/find", json=payload)

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_rejects_a_non_object_filter(client, credentialed_user, manager):
    _login(client)
    resp = client.post(
        "/api/context/find", json={"query": "a", "filter": ["not", "an", "object"]}
    )

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_rejects_an_unknown_time_field(client, credentialed_user, manager):
    _login(client)
    resp = client.post(
        "/api/context/find", json={"query": "a", "time_field": "whenever"}
    )

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_surfaces_backend_failure_as_502(client, credentialed_user):
    """The store is an implementation detail; its errors are not the user's."""
    inst = MagicMock()
    inst.query = AsyncMock(side_effect=UnavailableError("backend down"))
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 502
    # The backend's own message must not leak into the response.
    assert "backend down" not in resp.text


async def test_find_reports_total(client, credentialed_user, manager):
    manager.query = AsyncMock(
        return_value=ContextQueryResults(query="alpha", results=[], total=42)
    )
    _login(client)
    resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 200
    assert resp.json()["total"] == 42


# ---------------------------------------------------------------------------
# GET /api/context/ls
# ---------------------------------------------------------------------------


async def test_ls_returns_file_listing(client, credentialed_user, manager):
    _login(client)
    resp = client.get("/api/context/ls")

    assert resp.status_code == 200
    assert resp.json() == ["alpha.md", "beta.md"]
    manager.list_files.assert_awaited_once()


async def test_ls_decrypts_stored_key_for_manager(client, credentialed_user):
    _login(client)
    inst = MagicMock()
    inst.list_files = AsyncMock(return_value=[])
    with patch("app.routes.context.OpenVikingManager", return_value=inst) as cls:
        client.get("/api/context/ls")

    assert cls.call_args.args[1] == "plain-user-key"


# ---------------------------------------------------------------------------
# Credential provisioning
#
# ``user`` (not ``credentialed_user``) has no stored credential, so these
# exercise the first-use path through ``get_user_ov_api_key``.
# ---------------------------------------------------------------------------


async def test_find_provisions_credential_on_first_use(client, user, manager):
    """A user with no stored key gets one minted transparently — still a 200."""
    register = AsyncMock(return_value={"user_key": "minted-key"})
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 200
    register.assert_awaited_once_with(USER_TOKEN["orcid"])


async def test_find_uses_freshly_minted_key_for_manager(client, user):
    register = AsyncMock(return_value={"user_key": "minted-key"})
    inst = MagicMock()
    inst.query = AsyncMock(return_value=QUERY_RESULTS)
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register), patch(
        "app.routes.context.OpenVikingManager", return_value=inst
    ) as cls:
        client.post("/api/context/find", json={"query": "alpha"})

    assert cls.call_args.args[1] == "minted-key"


async def test_find_returns_502_when_provisioning_fails(client, user, manager):
    """Backend failures surface as a generic 502, never as OV specifics."""
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 502
    detail = resp.json()["detail"]
    assert "openviking" not in detail.lower()
    manager.query.assert_not_awaited()


async def test_ls_returns_502_when_provisioning_fails(client, user, manager):
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = client.get("/api/context/ls")

    assert resp.status_code == 502
    manager.list_files.assert_not_awaited()


# ---------------------------------------------------------------------------
# POST /api/context/ingest_files
# ---------------------------------------------------------------------------


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    """Build an in-memory zip archive from ``{relative_path: content}``."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _ingest(
    client,
    *,
    project="My Project",
    members=None,
    manifest=None,
    archive=None,
    force=None,
):
    """Post an ingest request.

    Defaults to a one-file archive whose manifest lists exactly that file.
    ``manifest`` defaults to every member of the archive, so a test that only
    cares about the archive contents does not have to restate them. ``force``
    is omitted from the form unless set, so the default path exercises the
    route's own default.
    """
    members = {"notes.md": b"hi"} if members is None else members
    manifest = list(members) if manifest is None else manifest
    archive = _zip_bytes(members) if archive is None else archive
    manifest_bytes = (
        manifest if isinstance(manifest, bytes) else "\n".join(manifest).encode()
    )
    data = {"project": project}
    if force is not None:
        data["force"] = str(force).lower()
    return client.post(
        "/api/context/ingest_files",
        data=data,
        files={
            "archive": ("upload.zip", archive, "application/zip"),
            "manifest": ("manifest.txt", manifest_bytes, "text/plain"),
        },
    )


def _queued(n: int) -> ContextIngestResults:
    return ContextIngestResults(
        results=[
            IngestResult(relative_path=f"f{i}.md", status="queued", uri=f"viking://{i}")
            for i in range(n)
        ],
        queued=n,
        failed=0,
    )


@pytest.fixture
def ingest_manager():
    """Patch OpenVikingManager for the ingest path; yields the instance."""
    inst = MagicMock()
    inst.insert_files = AsyncMock(return_value=_queued(1))
    # Default to "nothing new" so status tests opt in to a refresh explicitly.
    inst.task_statuses = AsyncMock(return_value={})
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


def test_ingest_unauthenticated_returns_401(client):
    assert _ingest(client).status_code == 401


async def test_ingest_queues_file_and_returns_results(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client)

    assert resp.status_code == 200
    body = resp.json()
    assert body["queued"] == 1
    assert body["failed"] == 0
    ingest_manager.insert_files.assert_awaited_once()


async def test_ingest_targets_user_orcid_and_project_slug(
    client, credentialed_user, ingest_manager
):
    """The target root is keyed on the uploader's ORCiD, then the slug."""
    _login(client)
    _ingest(client, project="Acinetobacter ADP1 Explorer")

    root = ingest_manager.insert_files.await_args.kwargs["target_root"]
    assert root == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/acinetobacter_adp1_explorer"
    )


async def test_ingest_forwards_file_content_and_path(
    client, credentialed_user, ingest_manager
):
    _login(client)
    _ingest(client, members={"sub/dir/data.csv": b"a,b\n1,2\n"})

    sent = ingest_manager.insert_files.await_args.args[0]
    assert len(sent) == 1
    # Nested paths survive so the structure is preserved below the root.
    assert sent[0].relative_path == "sub/dir/data.csv"
    assert sent[0].content == b"a,b\n1,2\n"


async def test_ingest_accepts_multiple_files(client, credentialed_user, ingest_manager):
    ingest_manager.insert_files.return_value = _queued(3)
    _login(client)
    resp = _ingest(
        client, members={"a.md": b"a", "b.md": b"b", "c.md": b"c"}
    )

    assert resp.status_code == 200
    assert resp.json()["queued"] == 3
    assert len(ingest_manager.insert_files.await_args.args[0]) == 3


async def test_ingest_only_takes_files_named_by_the_manifest(
    client, credentialed_user, ingest_manager
):
    """The archive may carry more than it ingests — the manifest decides."""
    _login(client)
    resp = _ingest(
        client,
        members={"keep/a.md": b"a", "skip/b.md": b"b"},
        manifest=["keep/a.md"],
    )

    assert resp.status_code == 200
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["keep/a.md"]


async def test_ingest_ignores_blank_manifest_lines(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client, members={"a.md": b"a"}, manifest=b"\na.md\n\n  \n")

    assert resp.status_code == 200
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["a.md"]


async def test_ingest_deduplicates_repeated_manifest_paths(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client, members={"a.md": b"a"}, manifest=["a.md", "a.md"])

    assert resp.status_code == 200
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["a.md"]


async def test_ingest_rejects_unreadable_archive(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client, archive=b"not a zip file", manifest=["a.md"])

    assert resp.status_code == 400
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_rejects_archive_with_symlink(
    client, credentialed_user, ingest_manager
):
    """A symlink member could redirect a later write outside the temp root."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        info = zipfile.ZipInfo("link")
        info.external_attr = (0xA1FF) << 16
        zf.writestr(info, "/etc/passwd")
    _login(client)
    resp = _ingest(client, archive=buf.getvalue(), manifest=["link"])

    assert resp.status_code == 400
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_rejects_manifest_naming_a_missing_file(
    client, credentialed_user, ingest_manager
):
    """A manifest that names anything absent queues nothing at all."""
    _login(client)
    resp = _ingest(
        client, members={"a.md": b"a"}, manifest=["a.md", "gone.md"]
    )

    assert resp.status_code == 422
    assert "gone.md" in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_rejects_manifest_naming_a_directory(
    client, credentialed_user, ingest_manager
):
    """A directory is not an ingestable file, even though the path exists."""
    _login(client)
    resp = _ingest(client, members={"sub/a.md": b"a"}, manifest=["sub"])

    assert resp.status_code == 422
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_rejects_empty_manifest(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client, members={"a.md": b"a"}, manifest=b"\n  \n")

    assert resp.status_code == 422
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_reports_partial_failure_as_200(
    client, credentialed_user, ingest_manager
):
    """A partly-failed batch still returns 200 with the failures named."""
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[
            IngestResult(relative_path="a.md", status="queued", uri="viking://a"),
            IngestResult(relative_path="b.md", status="failed", reason="rejected"),
        ],
        queued=1,
        failed=1,
    )
    _login(client)
    resp = _ingest(client)

    assert resp.status_code == 200
    body = resp.json()
    assert (body["queued"], body["failed"]) == (1, 1)
    assert body["results"][1]["status"] == "failed"


async def test_ingest_creates_project_when_absent(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    resp = _ingest(client, project="Brand New Project")

    assert resp.status_code == 200
    created = await get_project_by_slug(
        db_session, credentialed_user.id, "brand_new_project"
    )
    assert created is not None
    # The human-readable form is preserved as the title.
    assert created.title == "Brand New Project"


async def test_ingest_reuses_existing_project(
    client, credentialed_user, ingest_manager, db_session
):
    existing = await create_user_project(
        db_session, credentialed_user.id, title="Existing", slug="existing_project"
    )
    _login(client)
    resp = _ingest(client, project="Existing Project")

    assert resp.status_code == 200
    projects = await get_projects_for_user(db_session, credentialed_user.id)
    assert [p.id for p in projects] == [existing.id]


async def test_ingest_rejects_unusable_project_name(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(client, project="!!!")

    assert resp.status_code == 422
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_sanitizes_traversal_in_manifest_path(
    client, credentialed_user, ingest_manager
):
    """Traversal segments are stripped, so a manifest cannot reach outside the
    archive — the sanitized path then has to exist in it like any other."""
    _login(client)
    resp = _ingest(client, members={"escape.md": b"b"}, manifest=["../../escape.md"])

    assert resp.status_code == 200
    sent = ingest_manager.insert_files.await_args.args[0]
    assert sent[0].relative_path == "escape.md"


async def test_ingest_rejects_unusable_manifest_path_without_queueing_any(
    client, credentialed_user, ingest_manager
):
    """A path that sanitizes to nothing fails the whole batch — nothing queued."""
    _login(client)
    resp = _ingest(client, members={"good.md": b"a"}, manifest=["good.md", ".."])

    assert resp.status_code == 422
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_enforces_file_count_cap(client, credentialed_user, ingest_manager):
    _login(client)
    with patch.object(get_settings(), "context_max_ingest_files", 2):
        resp = _ingest(client, members={f"f{i}.md": b"x" for i in range(3)})

    assert resp.status_code == 413
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_enforces_file_size_cap(client, credentialed_user, ingest_manager):
    _login(client)
    with patch.object(get_settings(), "context_max_file_bytes", 4):
        resp = _ingest(client, members={"big.md": b"way too long"})

    assert resp.status_code == 413
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_provisions_credential_on_first_use(client, user, ingest_manager):
    """An uncredentialed user gets a key minted, same as the read paths."""
    register = AsyncMock(return_value={"user_key": "minted-key"})
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = _ingest(client)

    assert resp.status_code == 200
    register.assert_awaited_once_with(USER_TOKEN["orcid"])


async def test_ingest_returns_502_when_provisioning_fails(
    client, user, ingest_manager
):
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    _login(client)
    with patch("app.context_manager.openviking.register_ov_user", register):
        resp = _ingest(client)

    assert resp.status_code == 502
    ingest_manager.insert_files.assert_not_awaited()


# ---------------------------------------------------------------------------
# GET /api/context/ingest_status/{batch_id}
# ---------------------------------------------------------------------------


def _queued_with_tasks(paths_and_tasks) -> ContextIngestResults:
    return ContextIngestResults(
        results=[
            IngestResult(
                relative_path=p,
                status="queued",
                uri=f"viking://root/{p}",
                task_id=t,
            )
            for p, t in paths_and_tasks
        ],
        queued=len(paths_and_tasks),
        failed=0,
    )


async def _start_batch(client, ingest_manager, paths_and_tasks) -> str:
    """Run an ingest and return its batch_id."""
    ingest_manager.insert_files.return_value = _queued_with_tasks(paths_and_tasks)
    resp = _ingest(client)
    assert resp.status_code == 200
    return resp.json()["batch_id"]


async def test_ingest_returns_a_batch_id(client, credentialed_user, ingest_manager):
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    assert batch_id


async def test_ingest_records_content_hash(
    client, credentialed_user, ingest_manager, db_session
):
    """The submitted bytes are hashed onto the batch row.

    This is what lets a later ingest tell whether identical content already
    landed, so the recorded value must be the hash of what was actually sent.
    """
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t1")])
    _login(client)
    resp = _ingest(client, members={"a.md": b"contents"})
    assert resp.status_code == 200

    batch = await get_ingest_batch(db_session, resp.json()["batch_id"])
    assert [f.content_sha256 for f in batch.files] == [
        hashlib.sha256(b"contents").hexdigest()
    ]


async def test_ingest_records_distinct_hashes_per_file(
    client, credentialed_user, ingest_manager, db_session
):
    """Each file is hashed independently, matched to it by relative path."""
    ingest_manager.insert_files.return_value = _queued_with_tasks(
        [("a.md", "t1"), ("sub/b.md", "t2")]
    )
    _login(client)
    resp = _ingest(client, members={"a.md": b"aaa", "sub/b.md": b"bbb"})
    assert resp.status_code == 200

    batch = await get_ingest_batch(db_session, resp.json()["batch_id"])
    recorded = {f.relative_path: f.content_sha256 for f in batch.files}
    assert recorded == {
        "a.md": hashlib.sha256(b"aaa").hexdigest(),
        "sub/b.md": hashlib.sha256(b"bbb").hexdigest(),
    }


async def test_ingest_records_no_hash_for_a_file_never_read(
    client, credentialed_user, ingest_manager, db_session
):
    """A result the manager reports for a path we never read carries no hash.

    Defensive: the hash must come from bytes this request actually handled, so
    an unmatched path records null rather than borrowing another file's hash.
    """
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[
            IngestResult(relative_path="a.md", status="queued", uri="viking://a"),
            IngestResult(relative_path="ghost.md", status="failed", reason="nope"),
        ],
        queued=1,
        failed=1,
    )
    _login(client)
    resp = _ingest(client, members={"a.md": b"aaa"})
    assert resp.status_code == 200

    batch = await get_ingest_batch(db_session, resp.json()["batch_id"])
    recorded = {f.relative_path: f.content_sha256 for f in batch.files}
    assert recorded["a.md"] == hashlib.sha256(b"aaa").hexdigest()
    assert recorded["ghost.md"] is None


def test_ingest_status_unauthenticated_returns_401(client):
    assert client.get("/api/context/ingest_status/anything").status_code == 401


async def test_ingest_status_unknown_batch_returns_404(client, credentialed_user):
    _login(client)
    assert client.get("/api/context/ingest_status/nope").status_code == 404


async def test_ingest_status_hides_another_users_batch(
    client, credentialed_user, ingest_manager, db_session
):
    """A foreign batch is 404, not 403 — a probe must not confirm it exists."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    other = BerilUser(orcid_id="0000-0009-8888-7777", display_name="Bob")
    db_session.add(other)
    await db_session.commit()
    batch = await get_ingest_batch(db_session, batch_id)
    batch.user_id = other.id
    await db_session.commit()

    assert client.get(f"/api/context/ingest_status/{batch_id}").status_code == 404


async def test_ingest_status_reports_refreshed_progress(
    client, credentialed_user, ingest_manager
):
    _login(client)
    batch_id = await _start_batch(
        client, ingest_manager, [("a.md", "t1"), ("b.md", "t2")]
    )

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None), "t2": ("processing", None)}
    )
    resp = client.get(f"/api/context/ingest_status/{batch_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "processing"
    assert body["counts"]["completed"] == 1
    assert body["counts"]["processing"] == 1
    assert {f["relative_path"]: f["status"] for f in body["files"]} == {
        "a.md": "completed",
        "b.md": "processing",
    }


async def test_ingest_status_completes_when_all_land(
    client, credentialed_user, ingest_manager
):
    _login(client)
    batch_id = await _start_batch(
        client, ingest_manager, [("a.md", "t1"), ("b.md", "t2")]
    )

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None), "t2": ("completed", None)}
    )
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["status"] == "completed"
    assert body["counts"]["completed"] == 2


async def test_ingest_status_failure_outranks_success(
    client, credentialed_user, ingest_manager
):
    """One failed file makes the batch failed, however many others landed."""
    _login(client)
    batch_id = await _start_batch(
        client, ingest_manager, [("a.md", "t1"), ("b.md", "t2")]
    )

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None), "t2": ("failed", "parse blew up")}
    )
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["status"] == "failed"
    failed = [f for f in body["files"] if f["status"] == "failed"][0]
    assert failed["error"] == "parse blew up"


async def test_ingest_status_does_not_repoll_terminal_files(
    client, credentialed_user, ingest_manager
):
    """A settled result survives the backend forgetting the task."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None)}
    )
    client.get(f"/api/context/ingest_status/{batch_id}")

    # Second poll: nothing is outstanding, so the backend is not consulted.
    ingest_manager.task_statuses.reset_mock()
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    ingest_manager.task_statuses.assert_not_awaited()
    assert body["status"] == "completed"


async def test_ingest_status_keeps_last_known_when_backend_unreachable(
    client, credentialed_user, ingest_manager
):
    """An unreachable backend must not erase what we already recorded."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(return_value={"t1": ("unknown", None)})
    resp = client.get(f"/api/context/ingest_status/{batch_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["files"][0]["status"] == "queued"
    assert body["status"] == "processing"


async def test_ingest_status_reports_submission_failure(
    client, credentialed_user, ingest_manager
):
    """A file that never queued has no task to poll and stays failed."""
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[
            IngestResult(
                relative_path="a.md", status="failed", reason="rejected", task_id=None
            )
        ],
        queued=0,
        failed=1,
    )
    _login(client)
    batch_id = _ingest(client).json()["batch_id"]

    ingest_manager.task_statuses = AsyncMock(return_value={})
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    ingest_manager.task_statuses.assert_not_awaited()
    assert body["status"] == "failed"
    assert body["files"][0]["error"] == "rejected"


async def test_ingest_status_includes_project_slug(
    client, credentialed_user, ingest_manager
):
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t1")])
    batch_id = _ingest(client, project="My Test Project").json()["batch_id"]

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None)}
    )
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["project"] == "my_test_project"


async def test_ingest_status_counts_cover_every_status(
    client, credentialed_user, ingest_manager
):
    """counts always carries every status key, so clients can index it blindly."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(
        return_value={"t1": ("completed", None)}
    )
    counts = client.get(f"/api/context/ingest_status/{batch_id}").json()["counts"]

    assert set(counts) == {
        "queued",
        "processing",
        "completed",
        "failed",
        "unknown",
        # Present for a stable mapping, though a skipped file never reaches a
        # batch: it is not submitted, so it writes no row.
        "skipped",
    }
    assert counts["skipped"] == 0


# ---------------------------------------------------------------------------
# Skip-on-unchanged (content hash)
# ---------------------------------------------------------------------------


async def _land(client, ingest_manager, db_session, members):
    """Ingest ``members`` and mark every resulting file completed.

    Leaves the project in the state the skip check reads: content whose latest
    record is ``completed`` with a hash.
    """
    ingest_manager.insert_files.return_value = _queued_with_tasks(
        [(p, f"task-{i}") for i, p in enumerate(sorted(members))]
    )
    resp = _ingest(client, members=members)
    assert resp.status_code == 200
    batch = await get_ingest_batch(db_session, resp.json()["batch_id"])
    for f in batch.files:
        f.status = "completed"
    await db_session.commit()
    return batch.id


async def test_ingest_skips_unchanged_file(
    client, credentialed_user, ingest_manager, db_session
):
    """Identical content that already completed is not re-sent."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.reset_mock()
    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.status_code == 200
    body = resp.json()
    assert (body["queued"], body["skipped"]) == (0, 1)
    assert body["results"][0]["status"] == "skipped"
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_resends_changed_content(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"before"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, members={"a.md": b"after"})

    assert resp.status_code == 200
    assert resp.json()["skipped"] == 0
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["a.md"]


async def test_ingest_sends_a_new_path(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("b.md", "t2")])
    resp = _ingest(client, members={"b.md": b"new"})

    assert resp.status_code == 200
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["b.md"]


async def test_ingest_resends_after_a_failure(
    client, credentialed_user, ingest_manager, db_session
):
    """The critical case: a failed file must re-ingest despite matching bytes.

    Otherwise a transient failure becomes permanent and the user's retry
    silently does nothing.
    """
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t1")])
    resp = _ingest(client, members={"a.md": b"same"})
    batch = await get_ingest_batch(db_session, resp.json()["batch_id"])
    for f in batch.files:
        f.status = "failed"
    await db_session.commit()

    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.status_code == 200
    assert resp.json()["skipped"] == 0
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["a.md"]


async def test_ingest_resends_while_still_queued(
    client, credentialed_user, ingest_manager, db_session
):
    """An in-flight file has not landed; its outcome is unknown."""
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t1")])
    _ingest(client, members={"a.md": b"same"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.json()["skipped"] == 0
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["a.md"]


async def test_ingest_resends_when_prior_hash_is_null(
    client, credentialed_user, ingest_manager, db_session
):
    """A pre-hash row gives no basis for comparison, so it re-ingests."""
    _login(client)
    batch_id = await _land(client, ingest_manager, db_session, {"a.md": b"same"})
    batch = await get_ingest_batch(db_session, batch_id)
    for f in batch.files:
        f.content_sha256 = None
    await db_session.commit()

    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.json()["skipped"] == 0
    ingest_manager.insert_files.assert_awaited()


async def test_ingest_uses_the_latest_record_for_a_path(
    client, credentialed_user, ingest_manager, db_session
):
    """Two batches for one path: the most recent hash decides."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"v1"})
    await _land(client, ingest_manager, db_session, {"a.md": b"v2"})

    ingest_manager.insert_files.reset_mock()
    # v2 is current, so it skips.
    assert _ingest(client, members={"a.md": b"v2"}).json()["skipped"] == 1
    ingest_manager.insert_files.assert_not_awaited()

    # v1 is stale, so it re-ingests.
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t9")])
    assert _ingest(client, members={"a.md": b"v1"}).json()["skipped"] == 0
    ingest_manager.insert_files.assert_awaited()


async def test_ingest_does_not_skip_across_projects(
    client, credentialed_user, ingest_manager, db_session
):
    """Identical content in another project is not this project's content."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, project="Other Project", members={"a.md": b"same"})

    assert resp.json()["skipped"] == 0
    ingest_manager.insert_files.assert_awaited()


async def test_force_reingests_unchanged_files(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same"}, force=True)

    assert resp.status_code == 200
    assert resp.json()["skipped"] == 0
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["a.md"]


async def test_ingest_all_skipped_returns_no_batch_id(
    client, credentialed_user, ingest_manager, db_session
):
    """Nothing submitted means no batch — that is success, not a lost handle."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.reset_mock()
    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["batch_id"] is None
    assert (body["queued"], body["failed"], body["skipped"]) == (0, 0, 1)
    ingest_manager.insert_files.assert_not_awaited()


async def test_ingest_mixed_batch_accounts_for_every_file(
    client, credentialed_user, ingest_manager, db_session
):
    """A partial skip still reports one result per manifest entry."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("b.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same", "b.md": b"new"})

    assert resp.status_code == 200
    body = resp.json()
    assert (body["queued"], body["skipped"]) == (1, 1)
    by_path = {r["relative_path"]: r["status"] for r in body["results"]}
    assert by_path == {"a.md": "queued", "b.md": "skipped"} or by_path == {
        "b.md": "queued",
        "a.md": "skipped",
    }
    # Only the submitted file was sent to the manager.
    sent = ingest_manager.insert_files.await_args.args[0]
    assert [f.relative_path for f in sent] == ["b.md"]


async def test_skipped_files_write_no_batch_rows(
    client, credentialed_user, ingest_manager, db_session
):
    """A skip is not an ingest attempt.

    Recording one would let it satisfy a later skip check even though nothing
    was ever indexed.
    """
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})

    ingest_manager.insert_files.return_value = _queued_with_tasks([("b.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same", "b.md": b"new"})

    batch = await get_ingest_batch(db_session, resp.json()["batch_id"])
    assert [f.relative_path for f in batch.files] == ["b.md"]
