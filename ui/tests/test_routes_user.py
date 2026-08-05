"""Tests for user identity routes (app.routes.user) — /api/user/whoami."""

import os
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.db.crud import (
    _hash_token,
    create_named_api_token,
    revoke_api_token,
)
from app.db.models import BerilUser, UserApiToken
from app.db.session import get_db
from app.main import create_app


# ---------------------------------------------------------------------------
# Shared fixtures — mirrors test_routes_account.py for the login helper
# ---------------------------------------------------------------------------

GOOD_TOKEN = {
    "access_token": "fake-access-token",
    "token_type": "bearer",
    "orcid": "0000-0001-2345-6789",
    "name": "Test Researcher",
}


def make_mock_oauth_client(token: dict | None = None):
    auth_url = (
        "https://sandbox.orcid.org/oauth/authorize"
        "?client_id=APP-TESTCLIENTID&scope=%2Fauthenticate"
        "&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000"
        "%2Fauth%2Forcid%2Fcallback&state=mock-state"
    )
    mock_instance = MagicMock()
    mock_instance.create_authorization_url = MagicMock(return_value=(auth_url, "mock-state"))
    mock_instance.fetch_token = AsyncMock(return_value=token or {})
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    return MagicMock(return_value=mock_instance), mock_instance


_ENV = {
    "BERIL_TEST_SKIP_LIFESPAN": "True",
    "BERIL_ORCID_CLIENT_ID": "APP-TESTCLIENTID",
    "BERIL_ORCID_CLIENT_SECRET": "test-secret",
    "BERIL_ORCID_BASE_URL": "https://sandbox.orcid.org",
    "BERIL_SESSION_SECRET_KEY": "test-session-secret",
}


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
async def beril_user(db_session):
    u = BerilUser(orcid_id=GOOD_TOKEN["orcid"], display_name=GOOD_TOKEN["name"])
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


def _login(client):
    """Drive the mock ORCiD callback to set a real session cookie."""
    mock_class, _ = make_mock_oauth_client(token=GOOD_TOKEN)
    with patch("app.routes.auth.AsyncOAuth2Client", mock_class):
        client.get(
            "/auth/orcid/callback",
            params={"code": "fake-code"},
            follow_redirects=False,
        )


# ---------------------------------------------------------------------------
# GET /api/user/whoami
# ---------------------------------------------------------------------------


class TestWhoami:
    def test_returns_401_when_unauthenticated(self, client):
        resp = client.get("/api/user/whoami")
        assert resp.status_code == 401

    def test_returns_identity_via_session_cookie(self, client, beril_user):
        _login(client)
        resp = client.get("/api/user/whoami")
        assert resp.status_code == 200
        assert resp.json() == {
            "orcid_id": GOOD_TOKEN["orcid"],
            "display_name": GOOD_TOKEN["name"],
        }

    async def test_returns_identity_via_bearer_token(
        self, client, beril_user, db_session
    ):
        raw_token, _ = await create_named_api_token(
            db_session, beril_user.id, name="cli"
        )
        resp = client.get(
            "/api/user/whoami",
            headers={"Authorization": f"Bearer {raw_token}"},
        )
        assert resp.status_code == 200
        assert resp.json() == {
            "orcid_id": GOOD_TOKEN["orcid"],
            "display_name": GOOD_TOKEN["name"],
        }

    async def test_expired_bearer_token_is_401(
        self, client, beril_user, db_session
    ):
        raw_token = "beril_expired_token_for_test"
        db_session.add(
            UserApiToken(
                user_id=beril_user.id,
                token_hash=_hash_token(raw_token),
                name="expired",
                expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
            )
        )
        await db_session.commit()

        resp = client.get(
            "/api/user/whoami",
            headers={"Authorization": f"Bearer {raw_token}"},
        )
        assert resp.status_code == 401

    async def test_revoked_bearer_token_is_401(
        self, client, beril_user, db_session
    ):
        raw_token, record = await create_named_api_token(
            db_session, beril_user.id, name="doomed"
        )
        await revoke_api_token(db_session, record.id, beril_user.id)

        resp = client.get(
            "/api/user/whoami",
            headers={"Authorization": f"Bearer {raw_token}"},
        )
        assert resp.status_code == 401

    def test_unknown_bearer_token_is_401(self, client):
        resp = client.get(
            "/api/user/whoami",
            headers={"Authorization": "Bearer beril_nope"},
        )
        assert resp.status_code == 401

    async def test_null_display_name_serializes_as_null(
        self, client, db_session
    ):
        user = BerilUser(orcid_id="0000-0001-9999-9999", display_name=None)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        raw_token, _ = await create_named_api_token(
            db_session, user.id, name="anon-user"
        )
        resp = client.get(
            "/api/user/whoami",
            headers={"Authorization": f"Bearer {raw_token}"},
        )
        assert resp.status_code == 200
        assert resp.json() == {
            "orcid_id": "0000-0001-9999-9999",
            "display_name": None,
        }
