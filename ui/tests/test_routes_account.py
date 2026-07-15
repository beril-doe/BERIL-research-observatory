"""Tests for user account routes (app.routes.account) — token management."""

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.db.crud import (
    create_named_api_token,
    list_api_tokens_for_user,
)
from app.db.models import BerilUser, UserApiToken
from app.db.session import get_db
from app.main import create_app


# ---------------------------------------------------------------------------
# Shared fixtures — mirrors test_routes_data.py so the login helper works
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


@pytest.fixture
async def other_user(db_session):
    u = BerilUser(orcid_id="0000-0002-9999-9999", display_name="Other User")
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
# GET /account/tokens
# ---------------------------------------------------------------------------


class TestAccountTokensPage:
    def test_redirects_when_not_logged_in(self, client):
        resp = client.get("/account/tokens", follow_redirects=False)
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["location"]

    def test_returns_200_when_logged_in(self, client, beril_user):
        _login(client)
        resp = client.get("/account/tokens")
        assert resp.status_code == 200
        assert "API Tokens" in resp.text

    async def test_lists_active_tokens(self, client, beril_user, db_session):
        _login(client)
        await create_named_api_token(db_session, beril_user.id, name="laptop")
        await create_named_api_token(db_session, beril_user.id, name="workstation")

        resp = client.get("/account/tokens")
        assert resp.status_code == 200
        assert "laptop" in resp.text
        assert "workstation" in resp.text

    async def test_hides_other_users_tokens(
        self, client, beril_user, other_user, db_session
    ):
        _login(client)
        await create_named_api_token(db_session, other_user.id, name="not-mine")

        resp = client.get("/account/tokens")
        assert "not-mine" not in resp.text

    async def test_hides_revoked_tokens(self, client, beril_user, db_session):
        from app.db.crud import revoke_api_token

        _login(client)
        _, record = await create_named_api_token(
            db_session, beril_user.id, name="dead"
        )
        await revoke_api_token(db_session, record.id, beril_user.id)

        resp = client.get("/account/tokens")
        assert "dead" not in resp.text


# ---------------------------------------------------------------------------
# POST /account/tokens (create)
# ---------------------------------------------------------------------------


class TestAccountTokensCreate:
    def test_rejects_unauthenticated(self, client):
        resp = client.post(
            "/account/tokens",
            data={"name": "test", "expires_in": "90"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["location"]

    async def test_creates_token_and_redirects(self, client, beril_user, db_session):
        _login(client)
        resp = client.post(
            "/account/tokens",
            data={"name": "laptop", "expires_in": "90"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert resp.headers["location"] == "/account/tokens"

        tokens = await list_api_tokens_for_user(db_session, beril_user.id)
        assert len(tokens) == 1
        assert tokens[0].name == "laptop"
        assert tokens[0].expires_at is not None

    async def test_shows_raw_token_once(self, client, beril_user, db_session):
        """The raw token appears in the response after creation, but never
        again on subsequent GETs."""
        _login(client)
        # Create → follow redirect → raw token visible.
        resp = client.post(
            "/account/tokens",
            data={"name": "laptop", "expires_in": "90"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        # The raw token should appear as a beril_-prefixed string.
        assert "beril_" in resp.text
        # Grab it for the follow-up assertion.
        import re
        match = re.search(r"beril_[a-f0-9]{48}", resp.text)
        assert match is not None
        raw_token = match.group(0)

        # Refresh the page — raw token no longer shown.
        resp2 = client.get("/account/tokens")
        assert raw_token not in resp2.text

    async def test_never_expires_option(self, client, beril_user, db_session):
        _login(client)
        client.post(
            "/account/tokens",
            data={"name": "forever", "expires_in": "never"},
            follow_redirects=False,
        )
        tokens = await list_api_tokens_for_user(db_session, beril_user.id)
        assert len(tokens) == 1
        assert tokens[0].expires_at is None

    async def test_blank_name_is_rejected(self, client, beril_user, db_session):
        _login(client)
        resp = client.post(
            "/account/tokens",
            data={"name": "   ", "expires_in": "90"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        tokens = await list_api_tokens_for_user(db_session, beril_user.id)
        assert tokens == []

    async def test_invalid_expiry_is_rejected(self, client, beril_user, db_session):
        _login(client)
        resp = client.post(
            "/account/tokens",
            data={"name": "sneaky", "expires_in": "9999"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        tokens = await list_api_tokens_for_user(db_session, beril_user.id)
        assert tokens == []


# ---------------------------------------------------------------------------
# POST /account/tokens/{id}/revoke
# ---------------------------------------------------------------------------


class TestAccountTokensRevoke:
    def test_rejects_unauthenticated(self, client):
        resp = client.post(
            "/account/tokens/no-such-id/revoke", follow_redirects=False
        )
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["location"]

    async def test_revokes_owned_token(self, client, beril_user, db_session):
        from sqlalchemy import select

        _login(client)
        _, record = await create_named_api_token(
            db_session, beril_user.id, name="doomed"
        )
        resp = client.post(
            f"/account/tokens/{record.id}/revoke", follow_redirects=False
        )
        assert resp.status_code == 302

        result = await db_session.execute(
            select(UserApiToken).where(UserApiToken.id == record.id)
        )
        refreshed = result.scalar_one()
        assert refreshed.revoked_at is not None

    async def test_does_not_revoke_other_users_token(
        self, client, beril_user, other_user, db_session
    ):
        from sqlalchemy import select

        _login(client)
        _, record = await create_named_api_token(
            db_session, other_user.id, name="not-mine"
        )
        resp = client.post(
            f"/account/tokens/{record.id}/revoke", follow_redirects=False
        )
        # Redirects either way — silently no-ops rather than leaking existence.
        assert resp.status_code == 302

        result = await db_session.execute(
            select(UserApiToken).where(UserApiToken.id == record.id)
        )
        refreshed = result.scalar_one()
        assert refreshed.revoked_at is None

    async def test_revoke_unknown_id_is_noop(self, client, beril_user):
        _login(client)
        resp = client.post(
            "/account/tokens/nonexistent-id/revoke", follow_redirects=False
        )
        assert resp.status_code == 302
