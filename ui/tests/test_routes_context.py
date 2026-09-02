"""Tests for the context-manager routes (``/api/context/*``).

These exercise the route layer only: auth, credential lookup, decryption of the
stored per-user key, and request/response shaping. ``OpenVikingManager`` is
patched out, so no OpenViking instance is needed. The end-to-end mapping from an
OV payload to ``ContextQueryResults`` is covered in ``test_context_manager.py``.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.context_manager.base import ContextQueryResults, QueryResult
from app.crypto import encrypt_secret
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
