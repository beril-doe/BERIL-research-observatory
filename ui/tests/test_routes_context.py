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
from contextlib import nullcontext
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from openviking_sdk.errors import NotFoundError, UnavailableError

from app.clients.openviking import OpenVikingError
from app.config import get_settings
from app.context_manager.base import (
    MAX_OWNER_EXPANSION,
    ContextIngestResults,
    ContextQueryResults,
    IngestResult,
    QueryResult,
)
from app.context_manager.openviking import ContextUnavailableError
from app.crypto import encrypt_secret
from app.db.crud import (
    create_ingest_batch,
    create_user_project,
    get_ingest_batch,
    get_project_by_slug,
    get_projects_for_user,
    projects_with_memory,
)
from app.db.models import BerilUser, OvUserCredential, UserRole
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
            uri="viking://resources/users/0000-0001-2345-6789/alpha/REPORT.md",
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
    inst.grep = AsyncMock(
        return_value={"matches": [], "count": 0, "match_count": 0, "files_scanned": 0}
    )
    inst.glob = AsyncMock(return_value=[])
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


def _find_target(manager):
    """The resolved target the route handed to ``manager.query``."""
    return manager.query.await_args.kwargs["target_uri"]


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
            # The backend URI leaves as an address: owner/project/path.
            "address": "0000-0001-2345-6789/alpha/REPORT.md",
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
            "project": "alpha",
            "limit": 3,
            "score_threshold": 0.5,
        },
    )

    assert resp.status_code == 200
    sent = manager.query.await_args.args[0]
    assert sent.query == "alpha"
    assert sent.limit == 3
    assert sent.score_threshold == 0.5
    assert _find_target(manager) == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/alpha"
    )


async def test_find_applies_query_defaults(client, credentialed_user, manager):
    """Only ``query`` is required; the rest come from ContextQuery defaults."""
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})

    sent = manager.query.await_args.args[0]
    assert (sent.project, sent.owner, sent.all_owners, sent.path) == (
        None, None, False, None
    )
    assert sent.limit == 10
    assert sent.score_threshold is None


async def test_find_without_a_project_searches_the_whole_corpus(
    client, credentialed_user, manager
):
    """A bare query targets exactly the corpus root — not the caller's own
    namespace, and not the backend's default scope, which is wider."""
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})

    assert _find_target(manager) == "viking://resources/users"


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
            "since": "7d",
            "until": "2026-01-01",
            "time_field": "created_at",
            "node_limit": 50,
            "read_content": True,
        },
    )

    assert resp.status_code == 200
    sent = manager.query.await_args.args[0]
    assert (sent.since, sent.until, sent.time_field) == ("7d", "2026-01-01", "created_at")
    assert sent.node_limit == 50
    assert sent.read_content is True


async def test_find_applies_extended_defaults(client, credentialed_user, manager):
    """The new options are all opt-in; none changes behavior when omitted."""
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})

    sent = manager.query.await_args.args[0]
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


@pytest.mark.parametrize(
    "field, value",
    [
        ("root_path", "viking://resources"),
        ("filter", {"op": "must", "field": "uri", "conds": ["viking://x/"]}),
    ],
)
async def test_find_does_not_honor_a_raw_backend_scope(
    client, credentialed_user, manager, field, value
):
    """``root_path`` and ``filter`` are not part of the API.

    Either would let a caller name a backend location directly — outside the
    corpus, or through a filter tree BERIL cannot bound — so neither reaches
    the manager. Scope is addressed by project/owner/path, like ``/ls``.
    """
    _login(client)
    resp = client.post("/api/context/find", json={"query": "a", field: value})

    assert resp.status_code == 200
    assert _find_target(manager) == "viking://resources/users"
    assert not hasattr(manager.query.await_args.args[0], field)


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


async def test_ls_without_a_project_lists_the_users_namespace(
    client, credentialed_user, manager
):
    _login(client)
    client.get("/api/context/ls")

    uri = manager.list_files.await_args.args[0]
    assert uri == f"viking://resources/users/{USER_TOKEN['orcid']}"


async def test_ls_scopes_a_project_to_the_caller(client, credentialed_user, manager):
    _login(client)
    client.get("/api/context/ls", params={"project": "Acinetobacter ADP1 Explorer"})

    uri = manager.list_files.await_args.args[0]
    # Slugified, and under the caller's own ORCiD.
    assert uri == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/acinetobacter_adp1_explorer"
    )


async def test_ls_appends_a_relative_path(client, credentialed_user, manager):
    _login(client)
    client.get("/api/context/ls", params={"project": "alpha", "path": "memories"})

    uri = manager.list_files.await_args.args[0]
    assert uri == f"viking://resources/users/{USER_TOKEN['orcid']}/alpha/memories"


async def test_ls_forwards_listing_options(client, credentialed_user, manager):
    _login(client)
    client.get(
        "/api/context/ls",
        params={"project": "alpha", "recursive": "true", "simple": "true",
                "node_limit": 50},
    )

    kwargs = manager.list_files.await_args.kwargs
    assert (kwargs["recursive"], kwargs["simple"], kwargs["node_limit"]) == (
        True, True, 50
    )


async def test_ls_applies_option_defaults(client, credentialed_user, manager):
    _login(client)
    client.get("/api/context/ls")

    kwargs = manager.list_files.await_args.kwargs
    assert (kwargs["recursive"], kwargs["simple"], kwargs["node_limit"]) == (
        False, False, None
    )


@pytest.mark.parametrize(
    "path",
    ["../0000-9999-9999-9999", "../../users/other", "..", "a/../../escape"],
)
async def test_ls_rejects_traversal_out_of_the_corpus(
    client, credentialed_user, manager, path
):
    """A path must not climb out of the corpus into the wider resource tree.

    Reads span owners, so the owner is not the boundary — but the corpus root
    is, and a traversal is refused before the backend is asked.
    """
    _login(client)
    resp = client.get(
        "/api/context/ls", params={"project": "alpha", "path": path}
    )

    assert resp.status_code == 422
    manager.list_files.assert_not_awaited()


async def test_ls_rejects_a_path_without_a_project(
    client, credentialed_user, manager
):
    """`path` alone would resolve against the namespace root."""
    _login(client)
    resp = client.get("/api/context/ls", params={"path": "memories"})

    assert resp.status_code == 422
    manager.list_files.assert_not_awaited()


async def test_ls_rejects_an_unusable_project_name(
    client, credentialed_user, manager
):
    _login(client)
    resp = client.get("/api/context/ls", params={"project": "!!!"})

    assert resp.status_code == 422
    manager.list_files.assert_not_awaited()


@pytest.mark.parametrize("node_limit", [0, 10_000_000])
async def test_ls_rejects_out_of_range_node_limit(
    client, credentialed_user, manager, node_limit
):
    _login(client)
    resp = client.get(
        "/api/context/ls", params={"node_limit": node_limit}
    )

    assert resp.status_code == 422
    manager.list_files.assert_not_awaited()


async def test_ls_does_not_use_a_caller_supplied_orcid(
    client, credentialed_user, manager
):
    """``orcid`` is not an API field — ``owner`` is.

    Reads are global, so naming another owner is allowed; this guards the
    vocabulary, not the scope. An unknown parameter is ignored, and the
    default (the caller's own) applies.
    """
    _login(client)
    client.get(
        "/api/context/ls",
        params={"project": "alpha", "orcid": "0000-0009-8888-7777"},
    )

    uri = manager.list_files.await_args.args[0]
    assert USER_TOKEN["orcid"] in uri
    assert "0000-0009-8888-7777" not in uri


async def test_ls_empty_listing_is_not_an_error(client, credentialed_user, manager):
    """An un-ingested project lists empty rather than 404."""
    manager.list_files = AsyncMock(return_value=[])
    _login(client)
    resp = client.get("/api/context/ls", params={"project": "never_ingested"})

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.parametrize("route", ["ls", "grep"])
async def test_an_unknown_project_is_empty_end_to_end(
    client, credentialed_user, route
):
    """Through the real manager: the backend raises not-found for a project it
    does not know, and the route answers 200-empty rather than 502."""
    sdk = MagicMock()
    sdk.initialize = AsyncMock()
    sdk.close = AsyncMock()
    sdk.ls = AsyncMock(side_effect=NotFoundError("viking://x"))
    sdk.grep = AsyncMock(side_effect=NotFoundError("viking://x"))
    _login(client)
    with patch("app.clients.openviking.AsyncHTTPClient", return_value=sdk):
        if route == "ls":
            resp = client.get("/api/context/ls", params={"project": "never_ingested"})
        else:
            resp = _grep(client, project="never_ingested")

    assert resp.status_code == 200
    assert resp.json() == (
        [] if route == "ls"
        else {"matches": [], "count": 0, "match_count": 0, "files_scanned": 0}
    )


async def test_ls_surfaces_backend_failure_as_502(client, credentialed_user):
    inst = MagicMock()
    inst.list_files = AsyncMock(side_effect=UnavailableError("backend down"))
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        resp = client.get("/api/context/ls")

    assert resp.status_code == 502
    assert "backend down" not in resp.text


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


@pytest.fixture(autouse=True)
def ungated(request):
    """Admit every submission past the ingest gate in this module.

    These tests cover what happens *after* a submission is admitted — skips,
    removals, batches, publishing — with free-form file names and no approval
    files, so their counts stay about the behavior under test. The gate itself
    (allowlist, approval, force-is-admin) is tested through the real route,
    unpatched, in the ``gated`` tests at the end of this module and in
    ``test_ingest_gate.py``. Archive bounds are not patched out.
    """
    if request.node.get_closest_marker("gated"):
        yield
        return
    with patch("app.routes.context.disallowed", lambda paths: []), patch(
        "app.routes.context.APPROVAL_FILES", ()
    ), patch("app.routes.context.check_approval", lambda *a, **k: None):
        yield


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
    inst.remove_files = AsyncMock(side_effect=_removed_all)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


async def _removed_all(relative_paths, *, target_root):
    return [
        IngestResult(
            relative_path=p, status="removed", uri=f"{target_root}/{p}"
        )
        for p in relative_paths
    ]


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


async def test_ingest_creates_the_project_public(
    client, credentialed_user, ingest_manager, db_session
):
    """Ingest publishes: the corpus is readable by everyone, so the project
    page must not hide what ``/find`` already returns. ``is_public`` is the one
    visibility flag, and it is set rather than a second one introduced."""
    _login(client)
    _ingest(client, project="Brand New Project")

    created = await get_project_by_slug(
        db_session, credentialed_user.id, "brand_new_project"
    )
    assert created.is_public is True


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


async def test_ingest_publishes_a_reused_private_project(
    client, credentialed_user, ingest_manager, db_session
):
    """A private row that gets ingested into becomes public — its content is
    now in the corpus, whatever the flag said before."""
    existing = await create_user_project(
        db_session,
        credentialed_user.id,
        title="Existing",
        slug="existing_project",
        is_public=False,
    )
    assert existing.is_public is False
    _login(client)
    resp = _ingest(client, project="Existing Project")

    assert resp.status_code == 200
    await db_session.refresh(existing)
    assert existing.is_public is True


async def test_ingest_publishes_on_partial_success(
    client, credentialed_user, ingest_manager, db_session
):
    """One file queued is enough: that content is in the corpus."""
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[
            IngestResult(relative_path="a.md", status="queued", uri="viking://a"),
            IngestResult(relative_path="b.md", status="failed", reason="rejected"),
        ],
        queued=1,
        failed=1,
    )
    _login(client)
    _ingest(client, project="Brand New Project")

    created = await get_project_by_slug(
        db_session, credentialed_user.id, "brand_new_project"
    )
    assert created.is_public is True


def _all_rejected() -> ContextIngestResults:
    return ContextIngestResults(
        results=[IngestResult(relative_path="notes.md", status="failed", reason="no")],
        queued=0,
        failed=1,
    )


async def test_ingest_does_not_publish_when_every_file_is_rejected(
    client, credentialed_user, ingest_manager, db_session
):
    """Nothing reached the corpus, so nothing is published — a new row stays
    private and a reused private row is left as it was."""
    existing = await create_user_project(
        db_session, credentialed_user.id, title="Existing", slug="existing_project"
    )
    ingest_manager.insert_files.return_value = _all_rejected()
    _login(client)
    assert _ingest(client, project="Existing Project").status_code == 200
    assert _ingest(client, project="Brand New Project").status_code == 200

    await db_session.refresh(existing)
    assert existing.is_public is False
    created = await get_project_by_slug(
        db_session, credentialed_user.id, "brand_new_project"
    )
    assert created.is_public is False


_FAILING_SUBMISSIONS = {
    "unreadable archive": ({"archive": b"not a zip file", "manifest": ["a.md"]}, None),
    "manifest names a missing file": (
        {"members": {"a.md": b"a"}, "manifest": ["a.md", "gone.md"]}, None
    ),
    "too many files": (
        {"members": {f"f{i}.md": b"x" for i in range(3)}},
        ("context_max_ingest_files", 2),
    ),
    "file too large": (
        {"members": {"big.md": b"way too long"}}, ("context_max_file_bytes", 4)
    ),
}


@pytest.mark.parametrize("case", list(_FAILING_SUBMISSIONS))
async def test_a_rejected_submission_does_not_publish(
    client, credentialed_user, ingest_manager, db_session, case
):
    """Regression: publishing used to happen before validation, so a malformed
    upload made a private project public with nothing new in the corpus — and
    a first upload that failed left an empty public project in the listing."""
    kwargs, setting = _FAILING_SUBMISSIONS[case]
    existing = await create_user_project(
        db_session, credentialed_user.id, title="Existing", slug="existing_project"
    )
    _login(client)
    with (
        patch.object(get_settings(), *setting) if setting else nullcontext()
    ):
        reused = _ingest(client, project="Existing Project", **kwargs)
        fresh = _ingest(client, project="Brand New Project", **kwargs)

    assert reused.status_code >= 400 and fresh.status_code >= 400
    ingest_manager.insert_files.assert_not_awaited()
    await db_session.refresh(existing)
    assert existing.is_public is False
    created = await get_project_by_slug(
        db_session, credentialed_user.id, "brand_new_project"
    )
    assert created is None or created.is_public is False


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


@pytest.mark.parametrize(
    "failure",
    [
        ContextUnavailableError("rotated key refused"),
        UnavailableError("backend down"),
    ],
)
async def test_ingest_status_keeps_last_known_when_the_refresh_raises(
    client, credentialed_user, ingest_manager, failure
):
    """``task_statuses`` may now raise — a key that stayed refused after
    repair, or a failure before any poll ran. The status read still answers
    with what was recorded rather than failing."""
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(side_effect=failure)
    resp = client.get(f"/api/context/ingest_status/{batch_id}")

    assert resp.status_code == 200
    assert resp.json()["files"][0]["status"] == "queued"


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
        "expired",
        "unknown",
        # Present for a stable mapping, though a skipped file never reaches a
        # batch: it is not submitted, so it writes no row. Same for not_found.
        "skipped",
        "removed",
        "not_found",
    }
    assert counts["skipped"] == counts["not_found"] == 0


# ---------------------------------------------------------------------------
# Expired tasks: gone is not the same as unreachable
# ---------------------------------------------------------------------------


async def test_ingest_status_records_expired_and_stops_repolling(
    client, credentialed_user, ingest_manager
):
    """A task the backend has forgotten advances the row to a terminal state.

    Before the split, "gone" reported as ``unknown``, the route discarded it,
    and the row stayed ``queued`` — re-polled on every call with no way to
    ever advance. Now it lands as ``expired`` and is never asked about again.
    """
    _login(client)
    batch_id = await _start_batch(client, ingest_manager, [("a.md", "t1")])

    ingest_manager.task_statuses = AsyncMock(return_value={"t1": ("expired", None)})
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["files"][0]["status"] == "expired"
    assert body["status"] == "expired"

    # Terminal: the second poll has nothing outstanding and skips the backend.
    ingest_manager.task_statuses.reset_mock()
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    ingest_manager.task_statuses.assert_not_awaited()
    assert body["status"] == "expired"


async def test_expired_does_not_restore_the_skip(
    client, credentialed_user, ingest_manager, db_session
):
    """Expired is terminal but NOT completed, so identical content re-ingests.

    This is the deliberate limit of the split. Nothing proves the file landed,
    so a later submit must re-send rather than skip. Restoring the skip needs
    a reconcile against the store itself (does the target URI exist?) — the
    documented follow-up, not something this status implies.
    """
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t1")])
    batch_id = _ingest(client, members={"a.md": b"same"}).json()["batch_id"]

    ingest_manager.task_statuses = AsyncMock(return_value={"t1": ("expired", None)})
    assert client.get(f"/api/context/ingest_status/{batch_id}").json()["status"] == "expired"

    ingest_manager.insert_files.reset_mock()
    ingest_manager.insert_files.return_value = _queued_with_tasks([("a.md", "t2")])
    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.status_code == 200
    assert resp.json()["skipped"] == 0
    ingest_manager.insert_files.assert_awaited_once()


@pytest.mark.parametrize(
    "statuses, expected",
    [
        (["expired", "completed"], "expired"),
        (["expired", "unknown"], "expired"),
        (["expired", "processing"], "processing"),
        (["expired", "queued"], "processing"),
        (["expired", "failed"], "failed"),
        (["completed", "completed"], "completed"),
    ],
    ids=["beats-completed", "beats-unknown", "loses-to-processing",
         "loses-to-queued", "loses-to-failed", "clean-sweep"],
)
def test_rollup_ranks_expired_between_in_flight_and_unknown(statuses, expected):
    """Expired outranks unknown (the stronger non-answer) but never a live
    verdict: in-flight work and failure both win, and only an all-seen
    completion is a clean sweep."""
    from app.context_manager.base import IngestFileStatus
    from app.routes.context import _rollup_status

    files = [IngestFileStatus(relative_path=f"{i}.md", status=s) for i, s in enumerate(statuses)]

    assert _rollup_status(files) == expected


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
    """``force`` is an admin repair tool (see test_ingest_gate.py)."""
    db_session.add(UserRole(user_id=credentialed_user.id, role="admin"))
    await db_session.commit()
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


async def test_ingest_all_skipped_publishes(
    client, credentialed_user, ingest_manager, db_session
):
    """Nothing is sent, but a skip means identical content already completed
    for this project — it is in the corpus, so the project is published."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})
    project = await get_project_by_slug(db_session, credentialed_user.id, "my_project")
    project.is_public = False
    await db_session.commit()

    resp = _ingest(client, members={"a.md": b"same"})

    assert resp.json()["skipped"] == 1
    await db_session.refresh(project)
    assert project.is_public is True


async def test_ingest_publishes_when_the_rest_are_skipped(
    client, credentialed_user, ingest_manager, db_session
):
    """Every submitted file rejected, but a skipped one is already in the
    corpus — that alone publishes."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"a.md": b"same"})
    project = await get_project_by_slug(db_session, credentialed_user.id, "my_project")
    project.is_public = False
    await db_session.commit()

    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[IngestResult(relative_path="b.md", status="failed", reason="no")],
        queued=0,
        failed=1,
    )
    resp = _ingest(client, members={"a.md": b"same", "b.md": b"new"})

    assert (resp.json()["queued"], resp.json()["skipped"]) == (0, 1)
    await db_session.refresh(project)
    assert project.is_public is True


# ---------------------------------------------------------------------------
# Explicit removal: `!remove <path>` in the manifest
# ---------------------------------------------------------------------------

_MEMORY = "memories/discoveries.md"


async def test_ingest_removes_an_explicitly_named_file(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})

    resp = _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"])

    assert resp.status_code == 200
    body = resp.json()
    assert (body["removed"], body["queued"], body["failed"]) == (1, 0, 0)
    assert body["results"][0]["status"] == "removed"
    ingest_manager.remove_files.assert_awaited_once()
    assert ingest_manager.remove_files.await_args.args[0] == [_MEMORY]
    # Pinned to the caller's own namespace, like every write.
    assert ingest_manager.remove_files.await_args.kwargs["target_root"] == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/my_project"
    )
    # Recorded, so it supersedes the earlier completed row.
    batch = await get_ingest_batch(db_session, body["batch_id"])
    assert [(f.relative_path, f.status) for f in batch.files] == [(_MEMORY, "removed")]


async def test_ingest_leaves_files_absent_from_the_manifest_alone(
    client, credentialed_user, ingest_manager, db_session
):
    """Re-ingest is add-only: a missing path is not a removal."""
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})

    resp = _ingest(client, members={"README.md": b"new"})

    assert resp.status_code == 200
    assert resp.json()["removed"] == 0
    ingest_manager.remove_files.assert_not_awaited()


@pytest.mark.parametrize("already_removed", [False, True])
async def test_ingest_reports_not_found_for_a_path_the_project_does_not_hold(
    client, credentialed_user, ingest_manager, db_session, already_removed
):
    """Never ingested, or already removed: nothing to do, nothing recorded —
    so "remove if it exists" is idempotent."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"README.md": b"x"})
    if already_removed:
        await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})
        _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"])
        ingest_manager.remove_files.reset_mock()

    resp = _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"])

    assert resp.status_code == 200
    body = resp.json()
    assert (body["not_found"], body["removed"]) == (1, 0)
    assert body["results"][0]["status"] == "not_found"
    assert body["batch_id"] is None
    ingest_manager.remove_files.assert_not_awaited()


async def test_ingest_rejects_a_path_both_ingested_and_removed(
    client, credentialed_user, ingest_manager
):
    _login(client)
    resp = _ingest(
        client, members={_MEMORY: b"x"}, manifest=[_MEMORY, f"!remove {_MEMORY}"]
    )

    assert resp.status_code == 422
    assert _MEMORY in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()
    ingest_manager.remove_files.assert_not_awaited()


@pytest.mark.parametrize(
    "line", ["!delete memories/discoveries.md", "!remove", "!remove   ", "!REMOVE x.md"]
)
async def test_ingest_rejects_a_malformed_directive(
    client, credentialed_user, ingest_manager, line
):
    """An unknown or empty directive is refused, never read as a filename."""
    _login(client)
    resp = _ingest(client, members={}, manifest=[line])

    assert resp.status_code == 422
    ingest_manager.remove_files.assert_not_awaited()


@pytest.mark.parametrize(
    "path",
    [
        "../README.md",
        "./memories/discoveries.md",
        "memories/../README.md",
        "memories//discoveries.md",
        "/memories/discoveries.md",
        "memories\\discoveries.md",
    ],
)
async def test_ingest_rejects_a_removal_path_that_needs_repair(
    client, credentialed_user, ingest_manager, db_session, path
):
    """Regression (Codex, #451): sanitizing turned ``!remove ../README.md``
    into ``README.md`` and deleted a file the caller never named. Adds may be
    repaired; a destructive removal must name its file exactly."""
    _login(client)
    await _land(client, ingest_manager, db_session, {"README.md": b"r", _MEMORY: b"m"})

    resp = _ingest(client, members={}, manifest=[f"!remove {path}"])

    assert resp.status_code == 422
    assert "not a clean relative path" in resp.json()["detail"]
    ingest_manager.remove_files.assert_not_awaited()


async def test_ingest_still_repairs_a_path_being_added(
    client, credentialed_user, ingest_manager
):
    """Only removals are strict: an added path is still sanitized, as before."""
    _login(client)
    resp = _ingest(client, members={"notes.md": b"x"}, manifest=["./notes.md"])

    assert resp.status_code == 200
    assert ingest_manager.insert_files.await_args.args[0][0].relative_path == "notes.md"


def _fail_ingest(ingest_manager, path):
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[IngestResult(relative_path=path, status="failed", reason="no")],
        queued=0,
        failed=1,
    )


async def _remove(client, path):
    return _ingest(client, members={}, manifest=[f"!remove {path}"]).json()


async def test_removal_of_a_path_whose_only_ingest_failed_is_not_found(
    client, credentialed_user, ingest_manager
):
    """Regression (Codex, #451): the newest record was ``failed``, so the path
    counted as held; the backend deletes a missing path without complaint, so
    the route reported a withdrawal of a file that never landed."""
    _login(client)
    _fail_ingest(ingest_manager, _MEMORY)
    _ingest(client, members={_MEMORY: b"m"})

    body = await _remove(client, _MEMORY)

    assert (body["not_found"], body["removed"], body["batch_id"]) == (1, 0, None)
    ingest_manager.remove_files.assert_not_awaited()


async def test_removal_after_a_failed_readd_of_a_removed_path_is_not_found(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"m"})
    await _remove(client, _MEMORY)
    _fail_ingest(ingest_manager, _MEMORY)
    _ingest(client, members={_MEMORY: b"m2"})
    ingest_manager.remove_files.reset_mock()

    body = await _remove(client, _MEMORY)

    assert (body["not_found"], body["removed"]) == (1, 0)
    ingest_manager.remove_files.assert_not_awaited()


async def test_removal_after_a_failed_reingest_of_a_landed_file_removes_it(
    client, credentialed_user, ingest_manager, db_session
):
    """A failed re-ingest left the landed copy in place, so it is still held."""
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"m"})
    _fail_ingest(ingest_manager, _MEMORY)
    _ingest(client, members={_MEMORY: b"changed"})

    body = await _remove(client, _MEMORY)

    assert body["removed"] == 1
    assert ingest_manager.remove_files.await_args.args[0] == [_MEMORY]


async def test_removal_of_a_path_still_being_ingested_is_attempted(
    client, credentialed_user, ingest_manager
):
    """In flight is not assumed absent: the delete is tried, so the backend's
    refusal surfaces as "still being ingested" rather than a silent not_found."""
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([(_MEMORY, "t1")])
    _ingest(client, members={_MEMORY: b"m"})

    await _remove(client, _MEMORY)

    assert ingest_manager.remove_files.await_args.args[0] == [_MEMORY]


async def test_a_refused_removal_does_not_hide_an_ingest_that_later_lands(
    client, credentialed_user, ingest_manager
):
    """Regression (Codex, #451): the first ingest is queued and never polled
    (the mirror timed out); a removal is refused while it is in flight and
    recorded as failed; the ingest then lands. The failed removal used to be
    the newest record with nothing settled, so every later removal said
    not_found and the withdrawn file stayed searchable. Failed attempts are
    passed over now, so the queued ingest answers and the delete is tried."""
    _login(client)
    ingest_manager.insert_files.return_value = _queued_with_tasks([(_MEMORY, "t1")])
    _ingest(client, members={_MEMORY: b"m"})

    ingest_manager.remove_files.side_effect = None
    ingest_manager.remove_files.return_value = [
        IngestResult(
            relative_path=_MEMORY,
            status="failed",
            reason="This file is still being ingested; remove it again once that finishes.",
        )
    ]
    refused = await _remove(client, _MEMORY)
    assert refused["failed"] == 1

    # The ingest has since landed on the backend; nobody polled its batch.
    ingest_manager.remove_files.reset_mock()
    ingest_manager.remove_files.side_effect = _removed_all
    retried = await _remove(client, _MEMORY)

    assert (retried["removed"], retried["not_found"]) == (1, 0)
    assert ingest_manager.remove_files.await_args.args[0] == [_MEMORY]


async def test_ingest_records_a_failed_removal(
    client, credentialed_user, ingest_manager, db_session
):
    """A removal the backend refused is a failure the batch reports, and the
    file stays owned — its newest record is not ``removed``."""
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})
    ingest_manager.remove_files.side_effect = None
    ingest_manager.remove_files.return_value = [
        IngestResult(relative_path=_MEMORY, status="failed", reason="no")
    ]

    body = _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"]).json()

    assert (body["failed"], body["removed"]) == (1, 0)
    status_body = client.get(f"/api/context/ingest_status/{body['batch_id']}").json()
    assert status_body["status"] == "failed"
    assert await projects_with_memory(db_session, "discoveries") == {"my_project"}


async def test_a_removal_only_batch_rolls_up_completed(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})

    batch_id = _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"]).json()[
        "batch_id"
    ]
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["status"] == "completed"
    assert body["counts"]["removed"] == 1


async def test_ingest_removal_withdraws_memory_ownership(
    client, credentialed_user, ingest_manager, db_session
):
    """The point of the feature: a withdrawn memory stops suppressing the
    central legacy entry for its project."""
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})
    assert await projects_with_memory(db_session, "discoveries") == {"my_project"}

    _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"])

    assert await projects_with_memory(db_session, "discoveries") == set()


async def test_ingest_resends_a_file_added_back_after_removal(
    client, credentialed_user, ingest_manager, db_session
):
    """Identical content is not skipped once removed: it is no longer in the
    corpus, so the skip check must not match it."""
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})
    _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"])
    ingest_manager.insert_files.reset_mock()

    resp = _ingest(client, members={_MEMORY: b"finding"})

    assert resp.json()["skipped"] == 0
    ingest_manager.insert_files.assert_awaited_once()


async def test_a_removal_does_not_publish(
    client, credentialed_user, ingest_manager, db_session
):
    """Removal takes content out; it is never a reason to make a project public."""
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})
    project = await get_project_by_slug(db_session, credentialed_user.id, "my_project")
    project.is_public = False
    await db_session.commit()

    _ingest(client, members={}, manifest=[f"!remove {_MEMORY}"])

    await db_session.refresh(project)
    assert project.is_public is False


async def test_ingest_counts_removals_against_the_entry_cap(
    client, credentialed_user, ingest_manager
):
    _login(client)
    with patch.object(get_settings(), "context_max_ingest_files", 2):
        resp = _ingest(
            client,
            members={"a.md": b"a", "b.md": b"b"},
            manifest=["a.md", "b.md", "!remove c.md"],
        )

    assert resp.status_code == 413
    ingest_manager.remove_files.assert_not_awaited()


async def test_ingest_adds_and_removes_in_one_submission(
    client, credentialed_user, ingest_manager, db_session
):
    _login(client)
    await _land(client, ingest_manager, db_session, {_MEMORY: b"finding"})
    ingest_manager.insert_files.return_value = _queued_with_tasks([("REPORT.md", "t9")])

    body = _ingest(
        client, members={"REPORT.md": b"r"}, manifest=["REPORT.md", f"!remove {_MEMORY}"]
    ).json()

    assert (body["queued"], body["removed"]) == (1, 1)
    batch = await get_ingest_batch(db_session, body["batch_id"])
    assert sorted((f.relative_path, f.status) for f in batch.files) == [
        ("REPORT.md", "queued"), (_MEMORY, "removed")
    ]


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


# ---------------------------------------------------------------------------
# GET /api/context/grep
# ---------------------------------------------------------------------------


def _grep(client, **params):
    params.setdefault("pattern", "metal binding")
    return client.get("/api/context/grep", params=params)


def test_grep_unauthenticated_returns_401(client):
    assert client.get("/api/context/grep", params={"pattern": "x"}).status_code == 401


async def test_grep_returns_the_backend_payload(client, credentialed_user, manager):
    payload = {
        "matches": [
            {
                "uri": "viking://resources/users/0009-1/alpha/REPORT.md",
                "line": 1,
                "content": "x",
            }
        ],
        "count": 1,
        "match_count": 1,
        "files_scanned": 3,
    }
    manager.grep = AsyncMock(return_value=payload)
    _login(client)
    resp = _grep(client)

    assert resp.status_code == 200
    # The backend's payload, with each match's URI rewritten as an address.
    assert resp.json() == {
        **payload,
        "matches": [{"address": "0009-1/alpha/REPORT.md", "line": 1, "content": "x"}],
    }


async def test_grep_requires_a_pattern(client, credentialed_user, manager):
    _login(client)
    resp = client.get("/api/context/grep")

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


async def test_grep_rejects_an_empty_pattern(client, credentialed_user, manager):
    _login(client)
    resp = _grep(client, pattern="")

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


async def test_grep_without_a_project_searches_the_users_namespace(
    client, credentialed_user, manager
):
    _login(client)
    _grep(client)

    uri, pattern = manager.grep.await_args.args
    assert uri == f"viking://resources/users/{USER_TOKEN['orcid']}"
    assert pattern == "metal binding"


async def test_grep_scopes_a_project_to_the_caller(client, credentialed_user, manager):
    _login(client)
    _grep(client, project="Acinetobacter ADP1 Explorer", path="memories")

    uri = manager.grep.await_args.args[0]
    assert uri == (
        f"viking://resources/users/{USER_TOKEN['orcid']}"
        "/acinetobacter_adp1_explorer/memories"
    )


async def test_grep_forwards_options(client, credentialed_user, manager):
    _login(client)
    _grep(client, case_insensitive="true", node_limit=25)

    kwargs = manager.grep.await_args.kwargs
    assert kwargs["case_insensitive"] is True
    assert kwargs["node_limit"] == 25


async def test_grep_applies_option_defaults(client, credentialed_user, manager):
    _login(client)
    _grep(client)

    kwargs = manager.grep.await_args.kwargs
    assert kwargs["case_insensitive"] is False
    assert kwargs["node_limit"] is None
    assert kwargs["exclude_uri"] is None


async def test_grep_scopes_the_exclusion_too(client, credentialed_user, manager):
    _login(client)
    _grep(client, project="alpha", exclude_project="beta", exclude_path="drafts")

    kwargs = manager.grep.await_args.kwargs
    assert kwargs["exclude_uri"] == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/beta/drafts"
    )


@pytest.mark.parametrize(
    "path", ["../0000-9999-9999-9999", "../../users/other", "..", "a/../../escape"]
)
async def test_grep_rejects_traversal_in_the_search_path(
    client, credentialed_user, manager, path
):
    _login(client)
    resp = _grep(client, project="alpha", path=path)

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


@pytest.mark.parametrize(
    "exclude_path", ["../0000-9999-9999-9999", "../../users/other", ".."]
)
async def test_grep_rejects_traversal_in_the_exclusion_path(
    client, credentialed_user, manager, exclude_path
):
    """The exclusion is a second attack surface, resolved like the first.

    An unscoped exclusion would let a caller probe for the existence of paths
    outside the corpus by watching whether results change.
    """
    _login(client)
    resp = _grep(client, project="alpha", exclude_project="beta",
                 exclude_path=exclude_path)

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


async def test_grep_rejects_an_exclude_path_without_an_exclude_project(
    client, credentialed_user, manager
):
    _login(client)
    resp = _grep(client, project="alpha", exclude_path="drafts")

    assert resp.status_code == 422
    assert "exclude_project" in resp.json()["detail"]
    manager.grep.assert_not_awaited()


async def test_grep_rejects_a_path_without_a_project(
    client, credentialed_user, manager
):
    _login(client)
    resp = _grep(client, path="memories")

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


async def test_grep_rejects_an_unusable_project_name(
    client, credentialed_user, manager
):
    _login(client)
    resp = _grep(client, project="!!!")

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


@pytest.mark.parametrize("node_limit", [0, 10_000_000])
async def test_grep_rejects_out_of_range_node_limit(
    client, credentialed_user, manager, node_limit
):
    _login(client)
    resp = _grep(client, node_limit=node_limit)

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


async def test_grep_does_not_use_a_caller_supplied_orcid(
    client, credentialed_user, manager
):
    """``orcid`` is not an API field — ``owner`` is (see the ``ls`` twin)."""
    _login(client)
    _grep(client, project="alpha", orcid="0000-0009-8888-7777")

    uri = manager.grep.await_args.args[0]
    assert USER_TOKEN["orcid"] in uri
    assert "0000-0009-8888-7777" not in uri


async def test_grep_surfaces_backend_failure_as_502(client, credentialed_user):
    inst = MagicMock()
    inst.grep = AsyncMock(side_effect=UnavailableError("backend down"))
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        resp = _grep(client)

    assert resp.status_code == 502
    assert "backend down" not in resp.text


# ---------------------------------------------------------------------------
# Global reads: owner / all_owners
# ---------------------------------------------------------------------------

OTHER_ORCID = "0000-0009-8888-7777"


async def test_ls_reads_another_owners_project(
    client, credentialed_user, manager
):
    """Reads are global — a submitted project is readable by everyone.

    This is the behavior the earlier caller-pinned version got wrong.
    """
    _login(client)
    resp = client.get(
        "/api/context/ls", params={"project": "alpha", "owner": OTHER_ORCID}
    )

    assert resp.status_code == 200
    uri = manager.list_files.await_args.args[0]
    assert uri == f"viking://resources/users/{OTHER_ORCID}/alpha"


async def test_ls_spans_every_owner(client, credentialed_user, manager):
    _login(client)
    resp = client.get("/api/context/ls", params={"all_owners": "true"})

    assert resp.status_code == 200
    assert manager.list_files.await_args.args[0] == "viking://resources/users"


async def test_ls_all_owners_expands_the_project_across_owners(
    client, credentialed_user, manager
):
    """"Project alpha, whoever owns it" — a name many owners may share is not
    an address, so the backend is asked which owners have it and each copy is
    listed. Dropping the name would silently widen the read to the corpus."""
    manager.glob.return_value = [
        f"viking://resources/users/{USER_TOKEN['orcid']}/alpha",
        f"viking://resources/users/{OTHER_ORCID}/alpha",
    ]
    _login(client)
    resp = client.get(
        "/api/context/ls", params={"project": "alpha", "all_owners": "true"}
    )

    assert resp.status_code == 200
    manager.glob.assert_awaited_once_with(
        "*/alpha", "viking://resources/users", node_limit=MAX_OWNER_EXPANSION + 1
    )
    assert manager.list_files.await_args.args[0] == manager.glob.return_value


async def test_ls_all_owners_keeps_the_path_below_the_project(
    client, credentialed_user, manager
):
    _login(client)
    client.get(
        "/api/context/ls",
        params={"project": "alpha", "path": "notes/2026", "all_owners": "true"},
    )

    manager.glob.assert_awaited_once_with(
        "*/alpha/notes/2026",
        "viking://resources/users",
        node_limit=MAX_OWNER_EXPANSION + 1,
    )


async def test_ls_all_owners_escapes_glob_characters_in_the_path(
    client, credentialed_user, manager
):
    """Only the owner segment is a wildcard; a path is matched literally."""
    _login(client)
    client.get(
        "/api/context/ls",
        params={"project": "alpha", "path": "a*b", "all_owners": "true"},
    )

    assert manager.glob.await_args.args[0] == "*/alpha/a[*]b"


async def test_ls_all_owners_with_no_copies_lists_nothing(
    client, credentialed_user, manager
):
    """No owner has the project: the listing is empty, and the manager is
    handed an empty target rather than a wider one."""
    manager.glob.return_value = []
    manager.list_files.return_value = []
    _login(client)
    resp = client.get(
        "/api/context/ls", params={"project": "alpha", "all_owners": "true"}
    )

    assert resp.status_code == 200
    assert resp.json() == []
    assert manager.list_files.await_args.args[0] == []


@pytest.mark.parametrize("path", ["..", "../other", "a/../../escape"])
async def test_ls_all_owners_rejects_traversal_in_the_path(
    client, credentialed_user, manager, path
):
    """The wildcard target gets the same traversal check as a concrete one."""
    _login(client)
    resp = client.get(
        "/api/context/ls",
        params={"project": "alpha", "path": path, "all_owners": "true"},
    )

    assert resp.status_code == 422
    manager.glob.assert_not_awaited()
    manager.list_files.assert_not_awaited()


async def test_ls_bare_project_defaults_to_the_caller(
    client, credentialed_user, manager
):
    """The safe default: a typo must not silently read someone else's work."""
    _login(client)
    client.get("/api/context/ls", params={"project": "alpha"})

    uri = manager.list_files.await_args.args[0]
    assert uri == f"viking://resources/users/{USER_TOKEN['orcid']}/alpha"


async def test_ls_rejects_owner_with_all_owners(
    client, credentialed_user, manager
):
    _login(client)
    resp = client.get(
        "/api/context/ls",
        params={"owner": OTHER_ORCID, "all_owners": "true"},
    )

    assert resp.status_code == 422
    manager.list_files.assert_not_awaited()


@pytest.mark.parametrize("bad_owner", ["../..", "..", "a/../../.."])
async def test_ls_rejects_traversal_in_the_owner(
    client, credentialed_user, manager, bad_owner
):
    """The owner is caller input too, so it gets the same traversal check.

    Without this, `?owner=../..` would climb out of the corpus into the wider
    resource tree.
    """
    _login(client)
    resp = client.get("/api/context/ls", params={"owner": bad_owner})

    assert resp.status_code == 422
    manager.list_files.assert_not_awaited()


async def test_grep_searches_another_owners_project(
    client, credentialed_user, manager
):
    _login(client)
    resp = _grep(client, project="alpha", owner=OTHER_ORCID)

    assert resp.status_code == 200
    uri = manager.grep.await_args.args[0]
    assert uri == f"viking://resources/users/{OTHER_ORCID}/alpha"


async def test_grep_spans_every_owner(client, credentialed_user, manager):
    _login(client)
    resp = _grep(client, all_owners="true")

    assert resp.status_code == 200
    assert manager.grep.await_args.args[0] == "viking://resources/users"


async def test_grep_all_owners_expands_the_project_across_owners(
    client, credentialed_user, manager
):
    manager.glob.return_value = [
        f"viking://resources/users/{USER_TOKEN['orcid']}/alpha",
        f"viking://resources/users/{OTHER_ORCID}/alpha",
    ]
    _login(client)
    resp = _grep(client, project="alpha", all_owners="true")

    assert resp.status_code == 200
    manager.glob.assert_awaited_once_with(
        "*/alpha", "viking://resources/users", node_limit=MAX_OWNER_EXPANSION + 1
    )
    assert manager.grep.await_args.args[0] == manager.glob.return_value


async def test_grep_all_owners_with_no_copies_matches_nothing(
    client, credentialed_user, manager
):
    manager.glob.return_value = []
    _login(client)
    resp = _grep(client, project="alpha", all_owners="true")

    assert resp.status_code == 200
    assert manager.grep.await_args.args[0] == []


async def test_grep_excludes_another_owners_project(
    client, credentialed_user, manager
):
    _login(client)
    _grep(
        client,
        all_owners="true",
        exclude_project="beta",
        exclude_owner=OTHER_ORCID,
    )

    kwargs = manager.grep.await_args.kwargs
    assert kwargs["exclude_uri"] == f"viking://resources/users/{OTHER_ORCID}/beta"


async def test_grep_exclude_owner_alone_scopes_that_owner(
    client, credentialed_user, manager
):
    """An exclude_owner with no project excludes that whole owner."""
    _login(client)
    _grep(client, all_owners="true", exclude_owner=OTHER_ORCID)

    kwargs = manager.grep.await_args.kwargs
    assert kwargs["exclude_uri"] == f"viking://resources/users/{OTHER_ORCID}"


@pytest.mark.parametrize("bad_owner", ["../..", ".."])
async def test_grep_rejects_traversal_in_the_exclude_owner(
    client, credentialed_user, manager, bad_owner
):
    _login(client)
    resp = _grep(client, all_owners="true", exclude_owner=bad_owner)

    assert resp.status_code == 422
    manager.grep.assert_not_awaited()


# ---------------------------------------------------------------------------
# POST /api/context/find — scoped like ls and grep
# ---------------------------------------------------------------------------


def _find(client, **body):
    return client.post("/api/context/find", json={"query": "alpha", **body})


async def test_find_bare_project_defaults_to_the_caller(
    client, credentialed_user, manager
):
    _login(client)
    _find(client, project="alpha")

    assert _find_target(manager) == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/alpha"
    )


async def test_find_searches_another_owners_project(
    client, credentialed_user, manager
):
    """Reads are global: ``owner`` narrows the target, it does not authorize."""
    _login(client)
    resp = _find(client, project="alpha", owner=OTHER_ORCID)

    assert resp.status_code == 200
    assert _find_target(manager) == f"viking://resources/users/{OTHER_ORCID}/alpha"


async def test_find_appends_a_relative_path(client, credentialed_user, manager):
    _login(client)
    _find(client, project="alpha", path="notes/2026")

    assert _find_target(manager) == (
        f"viking://resources/users/{USER_TOKEN['orcid']}/alpha/notes/2026"
    )


async def test_find_spans_every_owner(client, credentialed_user, manager):
    _login(client)
    resp = _find(client, all_owners=True)

    assert resp.status_code == 200
    assert _find_target(manager) == "viking://resources/users"


async def test_find_all_owners_expands_the_project_across_owners(
    client, credentialed_user, manager
):
    """The expanded list is handed to the manager as one target — the backend
    ranks across several URIs natively, so there is no fan-out here."""
    manager.glob.return_value = [
        f"viking://resources/users/{USER_TOKEN['orcid']}/alpha",
        f"viking://resources/users/{OTHER_ORCID}/alpha",
    ]
    _login(client)
    resp = _find(client, project="alpha", all_owners=True)

    assert resp.status_code == 200
    manager.glob.assert_awaited_once_with(
        "*/alpha", "viking://resources/users", node_limit=MAX_OWNER_EXPANSION + 1
    )
    assert _find_target(manager) == manager.glob.return_value


async def test_find_all_owners_with_no_copies_targets_nothing(
    client, credentialed_user, manager
):
    manager.glob.return_value = []
    _login(client)
    resp = _find(client, project="alpha", all_owners=True)

    assert resp.status_code == 200
    assert _find_target(manager) == []


async def test_find_rejects_owner_with_all_owners(
    client, credentialed_user, manager
):
    _login(client)
    resp = _find(client, owner=OTHER_ORCID, all_owners=True)

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_rejects_a_path_without_a_project(
    client, credentialed_user, manager
):
    _login(client)
    resp = _find(client, path="notes")

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


async def test_find_rejects_an_unusable_project_name(
    client, credentialed_user, manager
):
    _login(client)
    resp = _find(client, project="!!!")

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


@pytest.mark.parametrize(
    "path", ["../0000-9999-9999-9999", "../../users/other", "..", "a/../../escape"]
)
async def test_find_rejects_traversal_in_the_path(
    client, credentialed_user, manager, path
):
    """The corpus root is the boundary; it is refused before the backend is
    asked, and before the query could fall back to a wider scope."""
    _login(client)
    resp = _find(client, project="alpha", path=path)

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


@pytest.mark.parametrize("bad_owner", ["../..", "..", "a/../../.."])
async def test_find_rejects_traversal_in_the_owner(
    client, credentialed_user, manager, bad_owner
):
    _login(client)
    resp = _find(client, owner=bad_owner)

    assert resp.status_code == 422
    manager.query.assert_not_awaited()


def _owners(n: int) -> list[str]:
    return [f"viking://resources/users/0000-0000-0000-{i:04d}/alpha" for i in range(n)]


@pytest.mark.parametrize("route", ["ls", "grep", "find"])
async def test_all_owners_refuses_more_owners_than_the_cap(
    client, credentialed_user, manager, route
):
    """Past the cap the backend would stop matching and silently drop owners,
    so the read is refused and the caller asked to name one — nothing is read."""
    manager.glob.return_value = _owners(MAX_OWNER_EXPANSION + 1)
    _login(client)
    if route == "ls":
        resp = client.get(
            "/api/context/ls", params={"project": "alpha", "all_owners": "true"}
        )
    elif route == "grep":
        resp = _grep(client, project="alpha", all_owners="true")
    else:
        resp = _find(client, project="alpha", all_owners=True)

    assert resp.status_code == 422
    assert "owner" in resp.json()["detail"]
    manager.list_files.assert_not_awaited()
    manager.grep.assert_not_awaited()
    manager.query.assert_not_awaited()


async def test_all_owners_reads_exactly_the_cap(client, credentialed_user, manager):
    manager.glob.return_value = _owners(MAX_OWNER_EXPANSION)
    _login(client)
    resp = client.get(
        "/api/context/ls", params={"project": "alpha", "all_owners": "true"}
    )

    assert resp.status_code == 200
    assert len(manager.list_files.await_args.args[0]) == MAX_OWNER_EXPANSION


async def test_find_surfaces_glob_failure_as_502(client, credentialed_user, manager):
    """Expanding the owner wildcard is a backend call like any other."""
    manager.glob.side_effect = UnavailableError("backend down")
    _login(client)
    resp = _find(client, project="alpha", all_owners=True)

    assert resp.status_code == 502
    assert "backend down" not in resp.text
    manager.query.assert_not_awaited()


# ---------------------------------------------------------------------------
# GET /api/context/pitfalls
# ---------------------------------------------------------------------------

_CENTRAL_DOC = "viking://resources/users/beril/docs/pitfalls"
_MEMORY_DOC = "viking://resources/users/0009-1/alpha/memories/pitfalls.md"


def _pitfall_docs():
    return (
        [
            {"uri": _MEMORY_DOC, "score": 0.88, "excerpts": ["spark OOM"],
             "fragment_uris": [f"{_MEMORY_DOC}/c.md"]},
            {"uri": _CENTRAL_DOC, "score": 0.67, "excerpts": ["pandas"],
             "fragment_uris": [f"{_CENTRAL_DOC}/a.md", f"{_CENTRAL_DOC}/b.md"]},
        ],
        7,
        2,
    )


@pytest.fixture
def pitfall_manager():
    inst = MagicMock()
    inst.find_pitfalls = AsyncMock(return_value=_pitfall_docs())
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


def _pattern(pitfall_manager):
    return pitfall_manager.find_pitfalls.await_args.kwargs["memory_pattern"]


def test_pitfalls_unauthenticated_returns_401(client):
    assert client.get("/api/context/pitfalls").status_code == 401


async def test_pitfalls_classifies_origin(client, credentialed_user, pitfall_manager):
    """A caller must be able to tell a project's own note from the archive."""
    _login(client)
    resp = client.get("/api/context/pitfalls", params={"q": "spark"})

    assert resp.status_code == 200
    body = resp.json()
    assert [r["origin"] for r in body["results"]] == ["project_memory", "central"]
    assert body["results"][0]["project"] == "alpha"
    assert body["results"][0]["owner"] == "0009-1"
    # A central doc belongs to no project.
    assert body["results"][1]["project"] is None
    assert body["results"][1]["owner"] == "beril"


async def test_pitfalls_reports_fragments_scanned_and_total(
    client, credentialed_user, pitfall_manager
):
    _login(client)
    body = client.get("/api/context/pitfalls", params={"q": "x"}).json()

    # Two documents, seven underlying fragments.
    assert len(body["results"]) == 2
    assert body["fragments_scanned"] == 7
    assert body["total"] == 2


async def test_pitfalls_spans_every_projects_memory_by_default(
    client, credentialed_user, pitfall_manager
):
    """No project named: every owner's every project's pitfall memory."""
    _login(client)
    client.get("/api/context/pitfalls", params={"q": "spark"})

    assert _pattern(pitfall_manager) == "*/*/memories/pitfalls.md"


async def test_pitfalls_narrows_the_memories_to_a_project(
    client, credentialed_user, pitfall_manager
):
    """A bare project is the caller's own, like every other read."""
    _login(client)
    client.get("/api/context/pitfalls", params={"q": "x", "project": "alpha"})

    assert _pattern(pitfall_manager) == (
        f"{USER_TOKEN['orcid']}/alpha/memories/pitfalls.md"
    )


async def test_pitfalls_narrows_to_another_owners_project(
    client, credentialed_user, pitfall_manager
):
    """Reads are global, so another owner's pitfalls are readable."""
    _login(client)
    client.get(
        "/api/context/pitfalls",
        params={"q": "x", "project": "alpha", "owner": "0000-0009-8888-7777"},
    )

    assert _pattern(pitfall_manager) == "0000-0009-8888-7777/alpha/memories/pitfalls.md"


async def test_pitfalls_owner_alone_spans_that_owners_projects(
    client, credentialed_user, pitfall_manager
):
    _login(client)
    client.get(
        "/api/context/pitfalls", params={"q": "x", "owner": "0000-0009-8888-7777"}
    )

    assert _pattern(pitfall_manager) == "0000-0009-8888-7777/*/memories/pitfalls.md"


async def test_pitfalls_passes_exact_through(
    client, credentialed_user, pitfall_manager
):
    """Exact beats semantic for error strings — the tokens users paste."""
    _login(client)
    client.get("/api/context/pitfalls", params={"q": "maxResultSize", "exact": "true"})

    assert pitfall_manager.find_pitfalls.await_args.kwargs["exact"] is True


async def test_pitfalls_defaults_to_semantic(
    client, credentialed_user, pitfall_manager
):
    _login(client)
    client.get("/api/context/pitfalls", params={"q": "memory blew up"})

    assert pitfall_manager.find_pitfalls.await_args.kwargs["exact"] is False


async def test_pitfalls_without_q_lists_every_pitfall(
    client, credentialed_user, pitfall_manager
):
    """Omitting ``q`` is a listing — "what pitfalls do we know about?" —
    passed down as ``None`` so nothing is searched."""
    pitfall_manager.find_pitfalls.return_value = (
        [
            {"uri": _CENTRAL_DOC, "score": None, "excerpts": [], "fragment_uris": []},
            {"uri": _MEMORY_DOC, "score": None, "excerpts": [], "fragment_uris": []},
        ],
        0,
        2,
    )
    _login(client)
    resp = client.get("/api/context/pitfalls")

    assert resp.status_code == 200
    assert pitfall_manager.find_pitfalls.await_args.args[0] is None
    body = resp.json()
    assert body["query"] is None
    assert [r["score"] for r in body["results"]] == [None, None]
    assert (body["total"], body["fragments_scanned"]) == (2, 0)


@pytest.mark.parametrize("q", ["", "   "])
async def test_pitfalls_rejects_an_empty_q(
    client, credentialed_user, pitfall_manager, q
):
    """An empty ``q`` is a malformed query, not a request to list — and the
    backend would reject it anyway."""
    _login(client)
    resp = client.get("/api/context/pitfalls", params={"q": q})

    assert resp.status_code == 422
    assert "omit it" in resp.json()["detail"]
    pitfall_manager.find_pitfalls.assert_not_awaited()


@pytest.mark.parametrize("limit", [0, 500])
async def test_pitfalls_rejects_out_of_range_limit(
    client, credentialed_user, pitfall_manager, limit
):
    _login(client)
    resp = client.get("/api/context/pitfalls", params={"q": "x", "limit": limit})

    assert resp.status_code == 422
    pitfall_manager.find_pitfalls.assert_not_awaited()


@pytest.mark.parametrize(
    "params", [{"owner": "../.."}, {"project": "alpha", "owner": ".."}]
)
async def test_pitfalls_rejects_traversal_in_the_owner(
    client, credentialed_user, pitfall_manager, params
):
    _login(client)
    resp = client.get("/api/context/pitfalls", params={"q": "x", **params})

    assert resp.status_code == 422
    pitfall_manager.find_pitfalls.assert_not_awaited()


async def test_pitfalls_surfaces_backend_failure_as_502(client, credentialed_user):
    inst = MagicMock()
    inst.find_pitfalls = AsyncMock(side_effect=UnavailableError("backend down"))
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        resp = client.get("/api/context/pitfalls", params={"q": "x"})

    assert resp.status_code == 502
    assert "backend down" not in resp.text


# ---------------------------------------------------------------------------
# GET /api/context/discoveries
# ---------------------------------------------------------------------------

_DISC_CENTRAL = "viking://resources/users/beril/docs/discoveries"
_DISC_MEMORY = "viking://resources/users/0009-1/alpha/memories/discoveries.md"


@pytest.fixture
def discovery_manager():
    inst = MagicMock()
    inst.find_discoveries = AsyncMock(
        return_value=(
            [
                {"uri": _DISC_MEMORY, "score": 0.9, "excerpts": ["current"],
                 "fragment_uris": [f"{_DISC_MEMORY}/c.md"]},
                {"uri": _DISC_CENTRAL, "score": 0.7,
                 "excerpts": ["### [legacy_proj] older finding"],
                 "fragment_uris": [f"{_DISC_CENTRAL}/a.md"]},
            ],
            9,
        )
    )
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        yield inst


def test_discoveries_unauthenticated_returns_401(client):
    assert client.get("/api/context/discoveries").status_code == 401


async def test_discoveries_classifies_origin(
    client, credentialed_user, discovery_manager
):
    _login(client)
    resp = client.get("/api/context/discoveries", params={"q": "phage"})

    assert resp.status_code == 200
    body = resp.json()
    assert [r["origin"] for r in body["results"]] == [
        "project_memory",
        "central_legacy",
    ]
    assert body["results"][0]["project"] == "alpha"
    assert body["results"][1]["project"] == "legacy_proj"


async def test_discoveries_suppresses_stale_central_duplicates(
    client, credentialed_user, discovery_manager, db_session
):
    """A central entry tagged for a project that owns its memory is dropped.

    The precedence rule end-to-end: the DB says which projects have a landed
    memory, and the route uses that to dedup.
    """
    # A project whose memories/discoveries.md completed an ingest.
    project = await create_user_project(
        db_session, credentialed_user.id, title="Legacy Proj", slug="legacy_proj"
    )
    batch = await create_ingest_batch(
        db_session,
        user_id=credentialed_user.id,
        project_id=project.id,
        target_root="viking://x",
        files=[{"relative_path": "memories/discoveries.md", "status": "completed"}],
    )
    assert batch.id

    _login(client)
    body = client.get("/api/context/discoveries", params={"q": "phage"}).json()

    # The central entry named legacy_proj, which now owns its own copy.
    assert body["suppressed"] == 1
    assert [r["origin"] for r in body["results"]] == ["project_memory"]


async def test_discoveries_reports_counts(
    client, credentialed_user, discovery_manager
):
    _login(client)
    body = client.get("/api/context/discoveries", params={"q": "x"}).json()

    assert body["fragments_scanned"] == 9
    # Nothing suppressed: no project has a landed memory in this fixture.
    assert body["suppressed"] == 0


async def test_discoveries_spans_every_projects_memory_by_default(
    client, credentialed_user, discovery_manager
):
    _login(client)
    client.get("/api/context/discoveries", params={"q": "x"})

    assert discovery_manager.find_discoveries.await_args.kwargs["memory_pattern"] == (
        "*/*/memories/discoveries.md"
    )


async def test_discoveries_narrows_the_memories_to_a_project(
    client, credentialed_user, discovery_manager
):
    _login(client)
    client.get("/api/context/discoveries", params={"q": "x", "project": "alpha"})

    assert discovery_manager.find_discoveries.await_args.kwargs["memory_pattern"] == (
        f"{USER_TOKEN['orcid']}/alpha/memories/discoveries.md"
    )


async def test_discoveries_applies_precedence_before_the_limit(
    client, credentialed_user, discovery_manager, db_session
):
    """Regression (#443 review): with ``limit=1`` a higher-ranked stale central
    duplicate took the only slot, was then suppressed, and nothing came back
    even though the project's current copy matched."""
    discovery_manager.find_discoveries.return_value = (
        [
            {"uri": _DISC_CENTRAL, "score": 0.95,
             "excerpts": ["### [alpha] stale duplicate"],
             "fragment_uris": [f"{_DISC_CENTRAL}/a.md"]},
            {"uri": _DISC_MEMORY, "score": 0.6, "excerpts": ["current"],
             "fragment_uris": [f"{_DISC_MEMORY}/c.md"]},
        ],
        5,
    )
    _login(client)
    with patch(
        "app.routes.context.projects_with_memory", AsyncMock(return_value={"alpha"})
    ):
        body = client.get(
            "/api/context/discoveries", params={"q": "x", "limit": 1}
        ).json()

    assert [r["address"] for r in body["results"]] == [
        "0009-1/alpha/memories/discoveries.md"
    ]
    assert (body["suppressed"], body["total"]) == (1, 1)


async def test_discoveries_without_q_lists_every_discovery(
    client, credentialed_user, discovery_manager
):
    discovery_manager.find_discoveries.return_value = (
        [{"uri": _DISC_CENTRAL, "score": None, "excerpts": [], "fragment_uris": []}],
        0,
    )
    _login(client)
    resp = client.get("/api/context/discoveries")

    assert resp.status_code == 200
    assert discovery_manager.find_discoveries.await_args.args[0] is None
    assert resp.json()["results"][0]["score"] is None


@pytest.mark.parametrize("q", ["", "  "])
async def test_discoveries_rejects_an_empty_q(
    client, credentialed_user, discovery_manager, q
):
    _login(client)
    resp = client.get("/api/context/discoveries", params={"q": q})

    assert resp.status_code == 422
    discovery_manager.find_discoveries.assert_not_awaited()


async def test_discoveries_passes_exact_through(
    client, credentialed_user, discovery_manager
):
    _login(client)
    client.get("/api/context/discoveries", params={"q": "x", "exact": "true"})

    assert discovery_manager.find_discoveries.await_args.kwargs["exact"] is True


@pytest.mark.parametrize("limit", [0, 500])
async def test_discoveries_rejects_out_of_range_limit(
    client, credentialed_user, discovery_manager, limit
):
    _login(client)
    resp = client.get(
        "/api/context/discoveries", params={"q": "x", "limit": limit}
    )

    assert resp.status_code == 422
    discovery_manager.find_discoveries.assert_not_awaited()


async def test_discoveries_rejects_traversal_in_the_owner(
    client, credentialed_user, discovery_manager
):
    _login(client)
    resp = client.get(
        "/api/context/discoveries", params={"q": "x", "owner": "../.."}
    )

    assert resp.status_code == 422
    discovery_manager.find_discoveries.assert_not_awaited()


async def test_discoveries_surfaces_backend_failure_as_502(
    client, credentialed_user
):
    inst = MagicMock()
    inst.find_discoveries = AsyncMock(side_effect=UnavailableError("backend down"))
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        resp = client.get("/api/context/discoveries", params={"q": "x"})

    assert resp.status_code == 502
    assert "backend down" not in resp.text


# ---------------------------------------------------------------------------
# Credential lifecycle through the routes
# ---------------------------------------------------------------------------


async def test_find_reports_502_when_credential_encryption_fails(
    client, credentialed_user, manager
):
    """An unusable encryption key at runtime is a 502, not a traceback."""
    from app.crypto import CredentialEncryptionError

    _login(client)
    with patch(
        "app.routes.context.get_user_ov_api_key",
        AsyncMock(side_effect=CredentialEncryptionError("bad key material")),
    ):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 502
    assert "bad key material" not in resp.text
    manager.query.assert_not_awaited()


async def test_find_rotates_a_refused_key_and_retries(client, credentialed_user, manager):
    """A stored key the store refuses is rotated once and the call retried.

    Before, such a user got a 502 on every call with nothing pointing at the
    fix; now the first refusal repairs itself.
    """
    from openviking_sdk.errors import UnauthenticatedError as SdkUnauthenticated

    manager.query = AsyncMock(side_effect=[SdkUnauthenticated("revoked"), QUERY_RESULTS])
    regenerate = AsyncMock(return_value="fresh-key")
    _login(client)
    with patch("app.routes.context.regenerate_user_ov_api_key", regenerate):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 200
    assert resp.json()["query"] == "alpha"
    regenerate.assert_awaited_once()
    assert manager.query.await_count == 2
    # The retried call went out with the fresh key.
    assert manager.api_key == "fresh-key"



# ---------------------------------------------------------------------------
# An unrepairable store failure is a 502 on every route, never a 500
# ---------------------------------------------------------------------------


async def test_find_reports_an_unrepairable_store_as_502(client, credentialed_user):
    """Regression (Codex, #450): a failed key repair escaped the routes'
    QUERY_FAILURES catch and became a 500."""
    inst = MagicMock()
    inst.query = AsyncMock(side_effect=ContextUnavailableError("store down"))
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 502
    assert resp.json() == {"detail": "The context manager is currently unavailable."}
    assert "store down" not in resp.text


async def test_ingest_reports_an_unrepairable_store_as_502(
    client, credentialed_user, ingest_manager
):
    """The ingest route has no backend catch at all, so this was a 500."""
    ingest_manager.insert_files = AsyncMock(
        side_effect=ContextUnavailableError("rotated key refused")
    )
    _login(client)
    resp = _ingest(client)

    assert resp.status_code == 502
    assert "refused" not in resp.text


async def test_a_key_refused_after_rotation_is_a_502_end_to_end(
    client, credentialed_user
):
    """Through the real healer: the store refuses the stored key, the key is
    rotated, the store refuses the new one too — a 502, after one rotation."""
    from openviking_sdk.errors import UnauthenticatedError as SdkUnauthenticated

    inst = MagicMock()
    inst.query = AsyncMock(side_effect=SdkUnauthenticated("revoked"))
    regenerate = AsyncMock(return_value={"user_key": "fresh-key"})
    _login(client)
    with patch("app.routes.context.OpenVikingManager", return_value=inst), patch(
        "app.context_manager.openviking.regenerate_ov_user_key", regenerate
    ):
        resp = client.post("/api/context/find", json={"query": "alpha"})

    assert resp.status_code == 502
    regenerate.assert_awaited_once()
    assert inst.query.await_count == 2



# ---------------------------------------------------------------------------
# The ingest gate, through the real route (not patched out)
# ---------------------------------------------------------------------------

_REPORT = b"# Report\n\nFindings.\n"
_REVIEW = b"# Review\n\nLooks right.\n"


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _approved(
    *,
    project_id="My Project",
    status="complete",
    approver=USER_TOKEN["orcid"],
    report=_REPORT,
    review=_REVIEW,
    report_hash=None,
    review_hash=None,
    extra=None,
):
    """An approved project's archive members, as the mirror would send them."""
    manifest = {
        "project_id": project_id,
        "status": status,
        "approval": {
            "by": approver,
            "at": "2026-10-09T00:00:00Z",
            "report_hash": report_hash or _sha(_REPORT),
            "review": "REVIEW_1.md",
            "review_hash": review_hash or _sha(_REVIEW),
        },
    }
    members = {
        "beril.yaml": yaml.safe_dump(manifest).encode(),
        "REPORT.md": report,
        "REVIEW.md": review,
        "README.md": b"# My Project\n",
        "memories/pitfalls.md": b"# Pitfalls\n",
    }
    members.update(extra or {})
    return members


@pytest.mark.gated
async def test_gate_admits_an_approved_project_of_the_callers(
    client, credentialed_user, ingest_manager
):
    ingest_manager.insert_files.return_value = _queued(5)
    _login(client)
    resp = _ingest(client, members=_approved())

    assert resp.status_code == 200
    sent = {f.relative_path for f in ingest_manager.insert_files.await_args.args[0]}
    assert {"beril.yaml", "REPORT.md", "REVIEW.md"} <= sent


@pytest.mark.gated
@pytest.mark.parametrize(
    "members, code, fragment",
    [
        (_approved(status="reviewed"), 422, "not approved"),
        (_approved(approver="0000-0009-8888-7777"), 403, "approved by someone else"),
        (_approved(report=b"# Report\n\nEdited after approval.\n"), 422, "REPORT.md does not match"),
        (_approved(review=b"# Review\n\nRewritten.\n"), 422, "REVIEW.md does not match"),
        (_approved(report_hash="deadbeef"), 422, "not a sha256 hash"),
        (_approved(project_id="someone_elses_project"), 422, "names project"),
    ],
    ids=["not-complete", "other-approver", "report-edited", "review-edited",
         "bad-hash-format", "wrong-project"],
)
async def test_gate_refuses_an_unapproved_submission(
    client, credentialed_user, ingest_manager, db_session, members, code, fragment
):
    """Refused before anything else happens: no backend call, no project row."""
    _login(client)
    resp = _ingest(client, members=members)

    assert resp.status_code == code
    assert fragment in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()
    assert await get_projects_for_user(db_session, credentialed_user.id) == []


@pytest.mark.gated
async def test_gate_requires_the_approval_files_in_the_manifest(
    client, credentialed_user, ingest_manager
):
    """A submission cannot leave out the files it is checked against —
    including a removal-only one, since removals are writes too."""
    _login(client)
    members = _approved()
    resp = _ingest(
        client, members=members, manifest=["README.md", "!remove memories/old.md"]
    )

    assert resp.status_code == 422
    assert "approval files" in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()


@pytest.mark.gated
@pytest.mark.parametrize(
    "name", ["notes.md", "figures/plot.png", "data/table.csv", "memories/deep/x.md",
             "REFUTATION_0.md", "src/analysis.py"],
)
async def test_gate_refuses_files_the_mirror_never_stages(
    client, credentialed_user, ingest_manager, name
):
    _login(client)
    resp = _ingest(client, members=_approved(extra={name: b"x"}))

    assert resp.status_code == 422
    assert name in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()


@pytest.mark.gated
async def test_gate_admits_refutations_and_any_memory(
    client, credentialed_user, ingest_manager
):
    ingest_manager.insert_files.return_value = _queued(7)
    _login(client)
    resp = _ingest(
        client,
        members=_approved(extra={"REFUTATION_2.md": b"r", "memories/anything.md": b"m"}),
    )

    assert resp.status_code == 200


@pytest.mark.gated
async def test_gate_lets_a_removal_name_a_path_outside_the_allowlist(
    client, credentialed_user, ingest_manager
):
    """Files ingested before the allowlist can still be withdrawn."""
    _login(client)
    resp = _ingest(
        client,
        members=_approved(),
        manifest=[*_approved(), "!remove figures/old_plot.png"],
    )

    assert resp.status_code == 200
    assert resp.json()["not_found"] == 1


@pytest.mark.gated
async def test_force_requires_an_admin(client, credentialed_user, ingest_manager, db_session):
    _login(client)
    resp = _ingest(client, members=_approved(), force=True)

    assert resp.status_code == 403
    assert "administrator" in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()
    assert await get_projects_for_user(db_session, credentialed_user.id) == []


@pytest.mark.gated
async def test_force_is_allowed_for_an_admin(
    client, credentialed_user, ingest_manager, db_session
):
    db_session.add(UserRole(user_id=credentialed_user.id, role="admin"))
    await db_session.commit()
    ingest_manager.insert_files.return_value = _queued(5)
    _login(client)

    assert _ingest(client, members=_approved(), force=True).status_code == 200


@pytest.mark.gated
async def test_gate_refuses_an_oversized_upload_before_reading_it_all(
    client, credentialed_user, ingest_manager
):
    _login(client)
    with patch.object(get_settings(), "context_max_archive_bytes", 64):
        resp = _ingest(client, members=_approved())

    assert resp.status_code == 413
    assert "archive is too large" in resp.json()["detail"]


@pytest.mark.gated
async def test_gate_refuses_an_archive_that_expands_too_far(
    client, credentialed_user, ingest_manager
):
    """Bounded from the zip's own directory, before anything is inflated."""
    _login(client)
    bomb = _approved(extra={"memories/big.md": b"A" * 200_000})
    with patch.object(get_settings(), "context_max_expanded_bytes", 100_000):
        resp = _ingest(client, members=bomb)

    assert resp.status_code == 413
    assert "expands to" in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()


@pytest.mark.gated
async def test_gate_refuses_an_archive_with_too_many_entries(
    client, credentialed_user, ingest_manager, db_session
):
    """Unlisted padding entries count too — they cost memory the moment the
    archive is opened — so the limit (BERIL_CONTEXT_MAX_ARCHIVE_ENTRIES) is on
    the whole archive, checked before anything else is read from it."""
    _login(client)
    members = _approved()
    archive = _zip_bytes({**members, **{f"pad/{i}": b"" for i in range(50)}})
    with patch.object(get_settings(), "context_max_archive_entries", 20):
        resp = _ingest(client, members=members, archive=archive, manifest=list(members))

    assert resp.status_code == 413
    assert "entries" in resp.json()["detail"]
    ingest_manager.insert_files.assert_not_awaited()
    assert await get_projects_for_user(db_session, credentialed_user.id) == []


@pytest.mark.gated
async def test_gate_extracts_only_the_manifests_members(
    client, credentialed_user, ingest_manager
):
    """An archive may carry files the manifest does not name; they are never
    extracted, so they can neither be ingested nor count against the gate."""
    ingest_manager.insert_files.return_value = _queued(5)
    _login(client)
    members = _approved()
    archive = _zip_bytes({**members, "unlisted/secret.bin": b"\x00" * 10})

    resp = _ingest(client, members=members, archive=archive, manifest=list(members))

    assert resp.status_code == 200
    sent = {f.relative_path for f in ingest_manager.insert_files.await_args.args[0]}
    assert "unlisted/secret.bin" not in sent


# ---------------------------------------------------------------------------
# Addresses — no response names the backend
# ---------------------------------------------------------------------------

_OWNER = "0009-1"
_REPORT_URI = f"viking://resources/users/{_OWNER}/alpha/REPORT.md"


async def test_ls_entries_carry_addresses_not_uris(client, credentialed_user, manager):
    manager.list_files.return_value = [
        {"name": "REPORT.md", "isDir": False, "rel_path": "alpha/REPORT.md",
         "uri": _REPORT_URI},
    ]
    _login(client)
    body = client.get("/api/context/ls", params={"all_owners": True}).json()

    assert body == [
        {"name": "REPORT.md", "isDir": False, "rel_path": "alpha/REPORT.md",
         "address": f"{_OWNER}/alpha/REPORT.md"},
    ]


async def test_simple_ls_returns_bare_addresses(client, credentialed_user, manager):
    manager.list_files.return_value = [
        f"viking://resources/users/{_OWNER}",
        "viking://resources/users/beril",
    ]
    _login(client)
    body = client.get(
        "/api/context/ls", params={"all_owners": True, "simple": True}
    ).json()

    assert body == [_OWNER, "beril"]


async def test_pitfalls_name_documents_and_fragments_by_address(
    client, credentialed_user, pitfall_manager
):
    _login(client)
    body = client.get("/api/context/pitfalls", params={"q": "spark"}).json()

    memory = body["results"][0]
    assert memory["address"] == f"{_OWNER}/alpha/memories/pitfalls.md"
    assert memory["fragment_addresses"] == [f"{_OWNER}/alpha/memories/pitfalls.md/c.md"]
    assert "uri" not in memory and "fragment_uris" not in memory


async def test_ingest_results_carry_addresses(client, credentialed_user, ingest_manager):
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[IngestResult(relative_path="a.md", status="queued", uri=_REPORT_URI,
                              task_id="t1")],
        queued=1,
        failed=0,
    )
    _login(client)
    body = _ingest(client).json()

    assert body["results"][0]["address"] == f"{_OWNER}/alpha/REPORT.md"
    assert "uri" not in body["results"][0]


async def test_ingest_status_files_carry_addresses(
    client, credentialed_user, ingest_manager
):
    _login(client)
    ingest_manager.insert_files.return_value = ContextIngestResults(
        results=[IngestResult(relative_path="a.md", status="queued", uri=_REPORT_URI,
                              task_id="t1")],
        queued=1,
        failed=0,
    )
    batch_id = _ingest(client).json()["batch_id"]
    body = client.get(f"/api/context/ingest_status/{batch_id}").json()

    assert body["files"][0]["address"] == f"{_OWNER}/alpha/REPORT.md"


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("post", "/api/context/find", {"json": {"query": "alpha"}}),
        ("get", "/api/context/ls", {"params": {"all_owners": True}}),
        ("get", "/api/context/grep", {"params": {"pattern": "x", "all_owners": True}}),
    ],
)
async def test_read_routes_never_name_the_backend(
    client, credentialed_user, manager, method, path, kwargs
):
    manager.list_files.return_value = [{"name": "REPORT.md", "uri": _REPORT_URI}, _REPORT_URI]
    manager.grep.return_value = {
        "matches": [{"uri": _REPORT_URI, "line": 1, "content": "x"}],
        "count": 1, "match_count": 1, "files_scanned": 1,
    }
    _login(client)
    resp = getattr(client, method)(path, **kwargs)

    assert resp.status_code == 200
    assert "viking" not in resp.text


# ---------------------------------------------------------------------------
# GET /api/context/health
# ---------------------------------------------------------------------------


def test_health_requires_a_login(client):
    assert client.get("/api/context/health").status_code == 401


@pytest.mark.parametrize(("healthy", "status"), [(True, "ok"), (False, "unavailable")])
async def test_health_reports_the_store_without_naming_it(
    client, credentialed_user, healthy, status
):
    _login(client)
    with patch("app.routes.context.context_health", AsyncMock(return_value=healthy)):
        resp = client.get("/api/context/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": status}


# ---------------------------------------------------------------------------
# Admin import — repo projects indexed under their owners
# ---------------------------------------------------------------------------

_OWNER_ORCID = "0000-0003-1111-2222"


@pytest.fixture
def admin_store():
    """The store connection, and the class that built it (to see its key)."""
    inst = MagicMock()
    inst.insert_files = AsyncMock(return_value=_queued_with_tasks([("REPORT.md", "t1")]))
    inst.task_statuses = AsyncMock(return_value={})
    inst.remove_files = AsyncMock(side_effect=_removed_all)
    with patch("app.routes.context.OpenVikingManager", return_value=inst) as cls:
        yield inst, cls


async def _repo_project(db_session, slug="alpha_proj", *, owner_orcid=_OWNER_ORCID):
    """A project the repo importer created, owned per its rule."""
    from app.db.models import UserProject

    owner = BerilUser(orcid_id=owner_orcid, display_name="Owner")
    db_session.add(owner)
    await db_session.commit()
    project = UserProject(
        owner_id=owner.id, slug=slug, title=slug, origin="repo",
        repo_path=f"projects/{slug}", is_public=True,
    )
    db_session.add(project)
    await db_session.commit()
    return owner, project


async def _make_admin(db_session, user):
    db_session.add(UserRole(user_id=user.id, role="admin"))
    await db_session.commit()


def _import(client, *, project="alpha_proj", members=None, dry_run=None, archive=True):
    members = {"REPORT.md": b"# Report\n", "README.md": b"# Readme\n"} if members is None else members
    data = {"project": project}
    if dry_run is not None:
        data["dry_run"] = str(dry_run).lower()
    files = {
        "archive": ("upload.zip", _zip_bytes(members), "application/zip"),
        "manifest": ("manifest.txt", "\n".join(members).encode(), "text/plain"),
    } if archive else None
    return client.post("/api/admin/context/import_files", data=data, files=files)


@pytest.mark.gated
async def test_import_requires_an_admin(client, credentialed_user, db_session, admin_store):
    await _repo_project(db_session)
    _login(client)

    assert _import(client).status_code == 403
    admin_store[0].insert_files.assert_not_awaited()


@pytest.mark.gated
async def test_import_lands_in_the_owners_namespace_on_the_admin_key(
    client, credentialed_user, db_session, admin_store
):
    """No beril.yaml or approval is needed — these never went through
    /submit — and the files land under the *owner*, recorded on the owner's
    project and batch rows, written with BERIL's admin key."""
    from app.db.models import ContextIngestBatch

    inst, cls = admin_store
    owner, project = await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = _import(client)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert (body["project"], body["owner_orcid"], body["queued"]) == ("alpha_proj", _OWNER_ORCID, 1)
    assert inst.insert_files.await_args.kwargs["target_root"] == (
        f"viking://resources/users/{_OWNER_ORCID}/alpha_proj"
    )
    assert cls.call_args.args[1] == "admin-key"
    batch = await db_session.get(ContextIngestBatch, body["batch_id"])
    assert (batch.user_id, batch.project_id) == (owner.id, project.id)
    assert "viking" not in resp.text


@pytest.mark.gated
async def test_import_keeps_the_allowlist(client, credentialed_user, db_session, admin_store):
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = _import(client, members={"REPORT.md": b"r", "data/raw.csv": b"x"})

    assert resp.status_code == 422
    assert "data/raw.csv" in resp.json()["detail"]
    admin_store[0].insert_files.assert_not_awaited()


@pytest.mark.gated
async def test_import_refuses_a_project_the_importer_has_not_seen(
    client, credentialed_user, db_session, admin_store
):
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = _import(client, project="never_imported")

    assert resp.status_code == 404
    assert "repo import" in resp.json()["detail"]


@pytest.mark.gated
async def test_import_refuses_a_flagged_project(client, credentialed_user, db_session, admin_store):
    """No author ORCiD → the importer gave it to the sentinel; it is not
    indexed under anyone."""
    from app.importer import SENTINEL_ORCID

    await _repo_project(db_session, "orphan", owner_orcid=SENTINEL_ORCID)
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = _import(client, project="orphan")

    assert resp.status_code == 409
    assert "flagged" in resp.json()["detail"]
    admin_store[0].insert_files.assert_not_awaited()


@pytest.mark.gated
async def test_import_dry_run_reports_the_owner_and_touches_nothing(
    client, credentialed_user, db_session, admin_store
):
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = _import(client, dry_run=True, archive=False)

    assert resp.status_code == 200
    body = resp.json()
    assert (body["owner_orcid"], body["dry_run"], body["batch_id"]) == (_OWNER_ORCID, True, None)
    admin_store[1].assert_not_called()


@pytest.mark.gated
async def test_import_refuses_a_bad_directory_name(client, credentialed_user, db_session, admin_store):
    await _make_admin(db_session, credentialed_user)
    _login(client)

    assert _import(client, project="../etc").status_code == 422


@pytest.mark.gated
async def test_an_owners_own_submit_skips_what_the_import_landed(
    client, credentialed_user, db_session, admin_store
):
    """The import records under the owner, so their later /submit of the
    same, unchanged project sends nothing."""
    from sqlalchemy import update

    from app.db.models import ContextIngestFileRecord, UserProject

    inst, _cls = admin_store
    owner_project = UserProject(
        owner_id=credentialed_user.id, slug="mine", title="mine",
        origin="repo", repo_path="projects/mine", is_public=True,
    )
    db_session.add(owner_project)
    await _make_admin(db_session, credentialed_user)
    _login(client)
    members = _approved(project_id="mine")
    inst.insert_files.return_value = _queued_with_tasks(
        [(path, f"t{i}") for i, path in enumerate(members)]
    )
    resp = _import(client, project="mine", members=members)
    assert resp.status_code == 200, resp.text
    await db_session.execute(update(ContextIngestFileRecord).values(status="completed"))
    await db_session.commit()
    inst.insert_files.reset_mock()

    again = _ingest(client, project="mine", members=members)

    assert again.status_code == 200, again.text
    assert again.json()["skipped"] == len(members)
    inst.insert_files.assert_not_awaited()


@pytest.mark.gated
async def test_import_status_polls_any_batch_with_the_admin_key(
    client, credentialed_user, db_session, admin_store
):
    inst, cls = admin_store
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)
    batch_id = _import(client).json()["batch_id"]
    cls.reset_mock()
    inst.task_statuses = AsyncMock(return_value={"t1": ("completed", None)})

    resp = client.get(f"/api/admin/context/import_status/{batch_id}")

    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert cls.call_args.args[1] == "admin-key"
    # The importer is not the owner, so the user route still hides it.
    assert client.get(f"/api/context/ingest_status/{batch_id}").status_code == 404


async def test_import_status_requires_an_admin(client, credentialed_user):
    _login(client)
    assert client.get("/api/admin/context/import_status/whatever").status_code == 403


async def _imported_then_reowned(client, db_session, inst, members):
    """Import a repo project, settle it, then re-own it as the importer does."""
    from sqlalchemy import update

    from app.db.models import ContextIngestFileRecord

    old_owner, project = await _repo_project(db_session)
    inst.insert_files.return_value = _queued_with_tasks(
        [(p, f"t{i}") for i, p in enumerate(members)]
    )
    assert _import(client, members=members).status_code == 200
    await db_session.execute(update(ContextIngestFileRecord).values(status="completed"))
    new_owner = BerilUser(orcid_id="0000-0004-5555-6666", display_name="New")
    db_session.add(new_owner)
    await db_session.commit()
    project.owner_id = new_owner.id  # what the repo importer does on re-owning
    await db_session.commit()
    inst.insert_files.reset_mock()
    return old_owner, new_owner, project


_MEMBERS = {"REPORT.md": b"# Report\n", "README.md": b"# Readme\n"}


async def _land_everything(db_session):
    """Let every submitted file finish indexing."""
    from sqlalchemy import update

    from app.db.models import ContextIngestFileRecord

    await db_session.execute(
        update(ContextIngestFileRecord)
        .where(ContextIngestFileRecord.status == "queued")
        .values(status="completed")
    )
    await db_session.commit()


@pytest.mark.gated
async def test_a_reowned_project_is_written_to_the_new_owner_and_its_old_copy_planned_for_removal(
    client, credentialed_user, db_session, admin_store
):
    """Regression (Codex review): the importer re-owns a project in place, so
    its earlier completed records keep its id. The new owner's import must
    still send every file, and the old namespace's files are marked
    removal-pending and handed back — not deleted inside the request."""
    from sqlalchemy import select

    from app.db.models import ContextIngestFileRecord

    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    old_owner, _new, _project = await _imported_then_reowned(client, db_session, inst, _MEMBERS)

    body = _import(client, members=_MEMBERS).json()

    assert body["owner_orcid"] == "0000-0004-5555-6666" and body["skipped"] == 0
    sent = inst.insert_files.await_args
    assert {f.relative_path for f in sent.args[0]} == set(_MEMBERS)
    assert sent.kwargs["target_root"].endswith("/0000-0004-5555-6666/alpha_proj")
    inst.remove_files.assert_not_awaited()  # planned, not done here
    assert len(body["retire_records"]) == 2
    markers = (await db_session.execute(
        select(ContextIngestFileRecord).where(ContextIngestFileRecord.id.in_(body["retire_records"]))
    )).scalars().all()
    assert {m.status for m in markers} == {"unknown"}


@pytest.mark.gated
async def test_retire_file_removes_one_file_and_is_safe_to_repeat(
    client, credentialed_user, db_session, admin_store
):
    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    old_owner, _new, _project = await _imported_then_reowned(client, db_session, inst, _MEMBERS)
    records = _import(client, members=_MEMBERS).json()["retire_records"]
    await _land_everything(db_session)

    first = client.post(f"/api/admin/context/retire_file/{records[0]}")
    again = client.post(f"/api/admin/context/retire_file/{records[0]}")

    assert first.status_code == 200 and first.json()["status"] == "removed"
    assert again.json()["status"] == "removed"
    inst.remove_files.assert_awaited_once()
    assert inst.remove_files.await_args.kwargs["target_root"] == (
        f"viking://resources/users/{old_owner.orcid_id}/alpha_proj"
    )
    assert "viking" not in first.text

    for record in records[1:]:
        client.post(f"/api/admin/context/retire_file/{record}")
    inst.insert_files.reset_mock()
    settled = _import(client, members=_MEMBERS).json()
    assert settled["retire_records"] == []


@pytest.mark.gated
async def test_an_interrupted_retirement_never_hides_missing_files(
    client, credentialed_user, db_session, admin_store
):
    """Regression (found live): retirement was cut off part-way, recorded
    nothing, and when the owner moved back the import trusted the old
    completed records and skipped files that had been deleted. Pending
    markers are written *before* any delete, and they do not count as
    landed — so moving the owner back re-sends everything."""
    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    old_owner, _new, project = await _imported_then_reowned(client, db_session, inst, _MEMBERS)
    assert len(_import(client, members=_MEMBERS).json()["retire_records"]) == 2
    # The retirement never ran (or ran part-way). The owner moves back:
    project.owner_id = old_owner.id
    await db_session.commit()
    inst.insert_files.reset_mock()

    back = _import(client, members=_MEMBERS).json()

    assert back["skipped"] == 0
    assert {f.relative_path for f in inst.insert_files.await_args.args[0]} == set(_MEMBERS)


@pytest.mark.gated
async def test_retire_waits_for_the_new_owners_copy_to_land(
    client, credentialed_user, db_session, admin_store
):
    """Regression (Codex stop-gate): retiring while the new owner's import is
    still indexing — or after it failed — could leave no copy at all."""
    from sqlalchemy import update

    from app.db.models import ContextIngestFileRecord

    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    await _imported_then_reowned(client, db_session, inst, _MEMBERS)
    records = _import(client, members=_MEMBERS).json()["retire_records"]

    early = client.post(f"/api/admin/context/retire_file/{records[0]}")
    assert early.status_code == 409 and "has not landed" in early.json()["detail"]

    await db_session.execute(
        update(ContextIngestFileRecord)
        .where(ContextIngestFileRecord.status == "queued")
        .values(status="failed")
    )
    await db_session.commit()
    assert client.post(f"/api/admin/context/retire_file/{records[0]}").status_code == 409
    inst.remove_files.assert_not_awaited()


@pytest.mark.gated
async def test_a_failed_retirement_is_planned_again(
    client, credentialed_user, db_session, admin_store
):
    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    await _imported_then_reowned(client, db_session, inst, _MEMBERS)
    records = _import(client, members=_MEMBERS).json()["retire_records"]
    await _land_everything(db_session)

    async def refuse(paths, *, target_root):
        return [IngestResult(relative_path=p, status="failed", reason="busy") for p in paths]

    inst.remove_files.side_effect = refuse
    assert client.post(f"/api/admin/context/retire_file/{records[0]}").json()["status"] == "failed"

    replanned = _import(client, members=_MEMBERS).json()["retire_records"]
    assert len(replanned) == 2  # the failed one is still held, as is the untried one


@pytest.mark.gated
async def test_retire_file_refuses_the_current_namespace_and_non_admins(
    client, credentialed_user, db_session, admin_store
):
    from sqlalchemy import select

    from app.db.models import ContextIngestFileRecord

    inst, _cls = admin_store
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)
    assert _import(client).status_code == 200
    current = (await db_session.execute(select(ContextIngestFileRecord))).scalars().first()

    assert client.post(f"/api/admin/context/retire_file/{current.id}").status_code == 409
    inst.remove_files.assert_not_awaited()
    assert client.post("/api/admin/context/retire_file/nope").status_code == 404


async def test_retire_file_requires_an_admin(client, credentialed_user):
    _login(client)
    assert client.post("/api/admin/context/retire_file/whatever").status_code == 403


@pytest.mark.gated
async def test_retire_file_rechecks_ownership_right_before_deleting(
    client, credentialed_user, db_session, admin_store
):
    """Mitigation (Codex adversarial review): the project re-owned back to the
    old namespace after planning is refused at the last check, not deleted."""
    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    old_owner, _new, project = await _imported_then_reowned(client, db_session, inst, _MEMBERS)
    records = _import(client, members=_MEMBERS).json()["retire_records"]
    await _land_everything(db_session)
    project.owner_id = old_owner.id  # re-owned back before the retirement runs
    await db_session.commit()

    resp = client.post(f"/api/admin/context/retire_file/{records[0]}")

    assert resp.status_code == 409
    inst.remove_files.assert_not_awaited()


@pytest.mark.gated
async def test_a_file_the_project_no_longer_has_is_retired_without_waiting(
    client, credentialed_user, db_session, admin_store
):
    """Regression (Codex review on #468): a file deleted from the repo since
    the old owner's import is never sent to the new owner, so waiting for its
    new copy refused it forever and left it searchable under the old owner."""
    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    with_notes = {**_MEMBERS, "RESEARCH_PLAN.md": b"# Plan\n"}
    await _imported_then_reowned(client, db_session, inst, with_notes)
    # The plan was deleted from the repo; the new owner's import lacks it.
    inst.insert_files.return_value = _queued_with_tasks(
        [(p, f"n{i}") for i, p in enumerate(_MEMBERS)]
    )
    records = _import(client, members=_MEMBERS).json()["retire_records"]
    await _land_everything(db_session)
    statuses = {}
    for record in records:
        resp = client.post(f"/api/admin/context/retire_file/{record}")
        statuses[resp.json()["relative_path"]] = (resp.status_code, resp.json()["status"])

    assert statuses["RESEARCH_PLAN.md"] == (200, "removed")
    assert all(v == (200, "removed") for v in statuses.values())


@pytest.mark.gated
async def test_retirement_is_planned_only_after_the_import_recorded_its_files(
    client, credentialed_user, db_session, admin_store
):
    """A file sent in this import but not landed is still waited for — the
    'no record' exemption above must not apply to it."""
    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    await _imported_then_reowned(client, db_session, inst, _MEMBERS)
    records = _import(client, members=_MEMBERS).json()["retire_records"]

    resp = client.post(f"/api/admin/context/retire_file/{records[0]}")

    assert resp.status_code == 409
    inst.remove_files.assert_not_awaited()


@pytest.mark.gated
async def test_a_file_withdrawn_in_the_new_namespace_is_retired_too(
    client, credentialed_user, db_session, admin_store
):
    """Regression (Codex stop-gate on #468): an explicit removal in the new
    owner's import leaves a latest ``removed`` record there. Nothing is
    coming, so the old copy must not wait for it."""
    from app.db.crud import create_ingest_batch

    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    old_owner, new_owner, project = await _imported_then_reowned(
        client, db_session, inst, _MEMBERS
    )
    records = _import(client, members=_MEMBERS).json()["retire_records"]
    await _land_everything(db_session)
    # The new owner withdraws README.md in their own namespace.
    await create_ingest_batch(
        db_session, user_id=new_owner.id, project_id=project.id,
        target_root=f"viking://resources/users/{new_owner.orcid_id}/alpha_proj",
        files=[{"relative_path": "README.md", "uri": None, "ov_task_id": None,
                "status": "removed", "error": None, "content_sha256": None}],
    )

    results = {}
    for record in records:
        resp = client.post(f"/api/admin/context/retire_file/{record}")
        results[resp.json().get("relative_path")] = resp.status_code
    assert results == {"README.md": 200, "REPORT.md": 200}


@pytest.mark.gated
async def test_retiring_an_old_memory_copy_keeps_the_project_owning_its_memory(
    client, credentialed_user, db_session, admin_store
):
    """Regression (Codex review on #468): the old owner's retired memory
    records ``removed`` after the new owner's copy completed; read across
    namespaces, that newer removal made the project look memory-less and
    let stale central duplicates back into /discoveries."""
    from app.db.crud import projects_with_memory

    inst, _cls = admin_store
    await _make_admin(db_session, credentialed_user)
    _login(client)
    members = {**_MEMBERS, "memories/discoveries.md": b"## A finding\n"}
    await _imported_then_reowned(client, db_session, inst, members)
    inst.insert_files.return_value = _queued_with_tasks(
        [(p, f"n{i}") for i, p in enumerate(members)]
    )
    records = _import(client, members=members).json()["retire_records"]
    await _land_everything(db_session)
    for record in records:
        assert client.post(f"/api/admin/context/retire_file/{record}").status_code == 200

    assert "alpha_proj" in await projects_with_memory(db_session, "discoveries")


# ---------------------------------------------------------------------------
# Admin diagnostics: the store's queue, and BERIL's unfinished records
# ---------------------------------------------------------------------------

_QUEUE_TEXT = """+----------------+---------+-------------+-----------+----------+--------+-------+
|     Queue      | Pending | In Progress | Processed | Requeued | Errors | Total |
+----------------+---------+-------------+-----------+----------+--------+-------+
|   Embedding    |    0    |      0      |   5092    |    0     |   0    | 5092  |
|    Semantic    |   42    |      3      |   1377    |    26    |   1    | 1377  |
|     TOTAL      |   42    |      3      |   11726   |   4471   |   1    | 11726 |
+----------------+---------+-------------+-----------+----------+--------+-------+"""

_MODELS_TEXT = """Account: beril
Embedding dimension: 3072

VLM Models:
+----------------------------+----------+-------+---------+------------+----------+--------------------------+
|           Model            | Provider | Calls | Prompt  | Completion |  Total   |       Last Updated       |
+----------------------------+----------+-------+---------+------------+----------+--------------------------+
| vertex_ai/gemini-2.5-flash | litellm  | 3822  | 8714310 |  6861686   | 15575996 | 2026-10-21T20:26:57.600Z |
+----------------------------+----------+-------+---------+------------+----------+--------------------------+


Embedding Models:
+--------------------------------+----------+-------+---------+------------+---------+--------------------------+
|             Model              | Provider | Calls | Prompt  | Completion |  Total  |       Last Updated       |
+--------------------------------+----------+-------+---------+------------+---------+--------------------------+
| vertex_ai/gemini-embedding-001 | litellm  | 5499  | 5607778 |     0      | 5607778 | 2026-10-21T20:55:34.962Z |
+--------------------------------+----------+-------+---------+------------+---------+--------------------------+
"""


def test_status_tables_parse_into_rows():
    """The store's real status text (server 0.4.22), as data."""
    from app.context_manager.openviking import parse_status_tables

    queues = parse_status_tables(_QUEUE_TEXT)["table"]
    semantic = next(q for q in queues if q["queue"] == "Semantic")
    assert (semantic["pending"], semantic["in_progress"], semantic["errors"]) == (42, 3, 1)

    models = parse_status_tables(_MODELS_TEXT)
    assert set(models) == {"vlm_models", "embedding_models"}
    vlm = models["vlm_models"][0]
    assert (vlm["model"], vlm["calls"], vlm["last_updated"]) == (
        "vertex_ai/gemini-2.5-flash", 3822, "2026-10-21T20:26:57.600Z"
    )


async def test_store_activity_gathers_queues_models_and_tasks():
    from app.context_manager.openviking import OpenVikingManager

    fake = MagicMock()
    fake.queue_status = AsyncMock(return_value={"is_healthy": True, "status": _QUEUE_TEXT})
    fake.models_status = AsyncMock(return_value={"is_healthy": True, "status": _MODELS_TEXT})
    fake.list_tasks = AsyncMock(side_effect=lambda status, limit: (
        [{"task_id": "t9", "status": "failed", "error": "quota"}] if status == "failed" else []
    ))
    fake.close = AsyncMock()
    with patch("app.context_manager.openviking.OpenVikingClient.create", AsyncMock(return_value=fake)):
        activity = await OpenVikingManager(MagicMock(ov_url="http://ov"), "k").store_activity(task_limit=7)

    assert activity["healthy"] is True
    assert {q["queue"] for q in activity["queues"]} == {"Embedding", "Semantic", "TOTAL"}
    assert activity["task_counts"] == {"pending": 0, "running": 0, "failed": 1}
    assert activity["tasks"]["failed"][0]["error"] == "quota"
    assert {c.kwargs["limit"] for c in fake.list_tasks.await_args_list} == {7}
    fake.close.assert_awaited_once()


async def test_queue_requires_an_admin(client, credentialed_user, admin_store):
    _login(client)
    assert client.get("/api/admin/context/queue").status_code == 403
    admin_store[1].assert_not_called()


async def test_queue_reports_the_store_on_the_admin_key(
    client, credentialed_user, db_session, admin_store
):
    inst, cls = admin_store
    inst.store_activity = AsyncMock(return_value={"healthy": True, "queues": [], "models": {},
                                                  "task_counts": {}, "tasks": {}})
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = client.get("/api/admin/context/queue", params={"task_limit": 5})

    assert resp.status_code == 200 and resp.json()["healthy"] is True
    assert cls.call_args.args[1] == "admin-key"
    assert inst.store_activity.await_args.kwargs == {"task_limit": 5}


async def test_queue_reports_an_unreachable_store_as_502(
    client, credentialed_user, db_session, admin_store
):
    from app.context_manager.openviking import QUERY_FAILURES

    inst, _cls = admin_store
    inst.store_activity = AsyncMock(side_effect=QUERY_FAILURES[0]("down"))
    await _make_admin(db_session, credentialed_user)
    _login(client)

    resp = client.get("/api/admin/context/queue")

    assert resp.status_code == 502
    assert "down" not in resp.text


async def test_unfinished_requires_an_admin(client, credentialed_user):
    _login(client)
    assert client.get("/api/admin/context/unfinished").status_code == 403


@pytest.mark.gated
async def test_unfinished_lists_unsettled_records_oldest_first(
    client, credentialed_user, db_session, admin_store
):
    from sqlalchemy import update

    from app.db.models import ContextIngestFileRecord

    inst, _cls = admin_store
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)
    inst.insert_files.return_value = _queued_with_tasks([("REPORT.md", "t1"), ("README.md", "t2")])
    assert _import(client).status_code == 200
    await db_session.execute(
        update(ContextIngestFileRecord)
        .where(ContextIngestFileRecord.relative_path == "README.md")
        .values(status="completed")
    )
    await db_session.commit()

    body = client.get("/api/admin/context/unfinished").json()

    assert body["counts"] == {"queued": 1} and body["truncated"] is False
    [only] = body["files"]
    assert (only["project"], only["owner_orcid"], only["status"]) == (
        "alpha_proj", _OWNER_ORCID, "queued"
    )
    assert only["address"] == f"{_OWNER_ORCID}/alpha_proj/REPORT.md"
    assert client.get(
        "/api/admin/context/unfinished", params={"project": "elsewhere"}
    ).json()["files"] == []


@pytest.mark.gated
async def test_unfinished_reports_truncation_only_when_rows_were_left_out(
    client, credentialed_user, db_session, admin_store
):
    """Regression (Codex stop-gate): exactly ``limit`` rows read as truncated."""
    inst, _cls = admin_store
    await _repo_project(db_session)
    await _make_admin(db_session, credentialed_user)
    _login(client)
    inst.insert_files.return_value = _queued_with_tasks([("REPORT.md", "t1"), ("README.md", "t2")])
    assert _import(client).status_code == 200

    exact = client.get("/api/admin/context/unfinished", params={"limit": 2}).json()
    short = client.get("/api/admin/context/unfinished", params={"limit": 1}).json()

    assert (len(exact["files"]), exact["truncated"]) == (2, False)
    assert (len(short["files"]), short["truncated"]) == (1, True)
