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
from app.crypto import encrypt_secret
from app.db.crud import (
    create_ingest_batch,
    create_user_project,
    get_ingest_batch,
    get_project_by_slug,
    get_projects_for_user,
    projects_with_memory,
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
        "matches": [{"uri": "viking://x", "line": 1, "content": "x"}],
        "count": 1,
        "match_count": 1,
        "files_scanned": 3,
    }
    manager.grep = AsyncMock(return_value=payload)
    _login(client)
    resp = _grep(client)

    assert resp.status_code == 200
    assert resp.json() == payload


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

    assert [r["uri"] for r in body["results"]] == [_DISC_MEMORY]
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
