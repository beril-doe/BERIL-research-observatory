"""Tests for the OpenViking search routes.

``ov_search`` is monkeypatched throughout, so these run against the in-memory
SQLite DB with no live OV instance. A real Fernet key is set in the environment
so the stored credential encrypts and decrypts for real — the decrypt step is
part of the route under test.

Mirrors the fixture/login pattern in ``test_routes_openviking.py``.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.clients.openviking import OpenVikingError
from app.crypto import encrypt_secret
from app.db.models import BerilUser, OvUserCredential
from app.db.session import get_db
from app.main import create_app
from app.routes.search import MAX_LIMIT, RESOURCES_TARGET_URI

_FERNET_KEY = Fernet.generate_key().decode()

_ENV = {
    "BERIL_TEST_SKIP_LIFESPAN": "True",
    "BERIL_ORCID_CLIENT_ID": "APP-TESTCLIENTID",
    "BERIL_ORCID_CLIENT_SECRET": "test-secret",
    "BERIL_ORCID_BASE_URL": "https://sandbox.orcid.org",
    "BERIL_SESSION_SECRET_KEY": "test-session-secret",
    "BERIL_OV_URL": "http://ov.test:1933",
    "BERIL_OV_ACCOUNT_ID": "beril",
    "BERIL_OV_ADMIN_KEY": "admin-key",
    "BERIL_OV_CREDENTIAL_KEY": _FERNET_KEY,
}

USER_TOKEN = {
    "access_token": "fake-access-token",
    "token_type": "bearer",
    "orcid": "0000-0001-2345-6789",
    "name": "Alice Researcher",
}

# A representative OV `result` payload: the route reads `resources` and `total`.
OV_RESULT = {
    "total": 2,
    "resources": [
        {
            "uri": "viking://resources/projects/phage_defense_arsenal/REPORT/Results.md",
            "score": 0.91,
            "abstract": "Defense systems co-occur.",
        },
        {
            "uri": "viking://resources/projects/soil_frontier_genomics/README.md",
            "score": 0.42,
            "abstract": "Soil genomics overview.",
        },
    ],
    "memories": [],
    "skills": [],
}


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
async def user_with_credential(db_session, user):
    """A logged-in-able user whose OV key is stored encrypted, as in production."""
    db_session.add(
        OvUserCredential(
            user_id=user.id,
            account_id="beril",
            ov_user_id=user.orcid_id,
            encrypted_key=encrypt_secret("user-key-abc", _FERNET_KEY),
        )
    )
    await db_session.commit()
    return user


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_api_search_unauthenticated_returns_401(client):
    assert client.get("/api/search", params={"q": "phage"}).status_code == 401


def test_search_page_unauthenticated_redirects_to_login(client):
    resp = client.get("/search", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/auth/login?next=/search"


async def test_search_page_authenticated_renders(client, user):
    _login(client)
    resp = client.get("/search")
    assert resp.status_code == 200
    # The page is only the SSR shell; the island mounts client-side.
    assert "search-island-root" in resp.text


# ---------------------------------------------------------------------------
# Query validation
# ---------------------------------------------------------------------------


async def test_empty_query_returns_400_without_calling_ov(client, user_with_credential):
    _login(client)
    fake_search = AsyncMock()
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": ""})

    assert resp.status_code == 400
    assert resp.json()["error"] == "empty_query"
    fake_search.assert_not_awaited()


async def test_whitespace_only_query_returns_400(client, user_with_credential):
    _login(client)
    fake_search = AsyncMock()
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "   "})

    assert resp.status_code == 400
    assert resp.json()["error"] == "empty_query"
    fake_search.assert_not_awaited()


async def test_missing_q_param_returns_400(client, user_with_credential):
    """`q` defaults to "" rather than 422 — the island always sends it."""
    _login(client)
    with patch("app.routes.search.ov_search", AsyncMock()):
        resp = client.get("/api/search")
    assert resp.status_code == 400


async def test_query_is_trimmed_before_search(client, user_with_credential):
    _login(client)
    fake_search = AsyncMock(return_value=OV_RESULT)
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "  phage defense  "})

    assert resp.status_code == 200
    assert resp.json()["query"] == "phage defense"
    assert fake_search.await_args.args[1] == "phage defense"


# ---------------------------------------------------------------------------
# Limit clamping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        (1, 1),
        (10, 10),
        (MAX_LIMIT, MAX_LIMIT),
        (MAX_LIMIT + 1, MAX_LIMIT),  # above the ceiling
        (9999, MAX_LIMIT),
        (0, 1),  # below the floor
        (-5, 1),
    ],
)
async def test_limit_is_clamped(client, user_with_credential, requested, expected):
    _login(client)
    fake_search = AsyncMock(return_value=OV_RESULT)
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "phage", "limit": requested})

    assert resp.status_code == 200
    assert fake_search.await_args.kwargs["limit"] == expected


async def test_default_limit_when_unspecified(client, user_with_credential):
    _login(client)
    fake_search = AsyncMock(return_value=OV_RESULT)
    with patch("app.routes.search.ov_search", fake_search):
        client.get("/api/search", params={"q": "phage"})

    assert fake_search.await_args.kwargs["limit"] == 10


async def test_non_integer_limit_returns_422(client, user_with_credential):
    """FastAPI coerces `limit`; a non-numeric value is a validation error."""
    _login(client)
    with patch("app.routes.search.ov_search", AsyncMock()):
        resp = client.get("/api/search", params={"q": "phage", "limit": "abc"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Credential handling
# ---------------------------------------------------------------------------


async def test_no_credential_returns_409(client, user):
    """User exists but never provisioned an OV account."""
    _login(client)
    fake_search = AsyncMock()
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 409
    assert resp.json()["error"] == "no_credential"
    fake_search.assert_not_awaited()


async def test_undecryptable_credential_returns_500(client, user, db_session):
    """A key encrypted under a different Fernet key can't be read back."""
    db_session.add(
        OvUserCredential(
            user_id=user.id,
            account_id="beril",
            ov_user_id=user.orcid_id,
            encrypted_key=encrypt_secret("user-key-abc", Fernet.generate_key().decode()),
        )
    )
    await db_session.commit()

    _login(client)
    fake_search = AsyncMock()
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 500
    assert resp.json()["error"] == "decrypt_failed"
    fake_search.assert_not_awaited()


async def test_decrypted_key_is_passed_to_ov(client, user_with_credential):
    """The plaintext key reaches ov_search, and the shared corpus is targeted."""
    _login(client)
    fake_search = AsyncMock(return_value=OV_RESULT)
    with patch("app.routes.search.ov_search", fake_search):
        client.get("/api/search", params={"q": "phage"})

    assert fake_search.await_args.args[0] == "user-key-abc"
    assert fake_search.await_args.kwargs["target_uri"] == RESOURCES_TARGET_URI


async def test_credential_key_not_leaked_in_response(client, user_with_credential):
    _login(client)
    with patch("app.routes.search.ov_search", AsyncMock(return_value=OV_RESULT)):
        resp = client.get("/api/search", params={"q": "phage"})

    assert "user-key-abc" not in resp.text


# ---------------------------------------------------------------------------
# OpenViking failures
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status_code", [401, 403])
async def test_rejected_key_returns_502_auth_failed(client, user_with_credential, status_code):
    _login(client)
    fake_search = AsyncMock(
        side_effect=OpenVikingError("nope", status_code=status_code, code="UNAUTHORIZED")
    )
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 502
    assert resp.json()["error"] == "auth_failed"


async def test_other_ov_error_returns_502_search_failed(client, user_with_credential):
    _login(client)
    fake_search = AsyncMock(side_effect=OpenVikingError("boom", status_code=500))
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 502
    assert resp.json()["error"] == "search_failed"


async def test_transport_error_returns_502(client, user_with_credential):
    """An OpenVikingError with no status_code (transport failure) still lands cleanly."""
    _login(client)
    fake_search = AsyncMock(side_effect=OpenVikingError("connection refused"))
    with patch("app.routes.search.ov_search", fake_search):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 502
    assert resp.json()["error"] == "search_failed"
    # The message is surfaced to the user, not swallowed.
    assert "connection refused" in resp.json()["message"]


# ---------------------------------------------------------------------------
# Result shaping
# ---------------------------------------------------------------------------


async def test_happy_path_returns_trimmed_results(client, user_with_credential):
    _login(client)
    with patch("app.routes.search.ov_search", AsyncMock(return_value=OV_RESULT)):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "phage"
    assert body["total"] == 2
    assert body["results"] == [
        {
            "uri": "viking://resources/projects/phage_defense_arsenal/REPORT/Results.md",
            "score": 0.91,
            "abstract": "Defense systems co-occur.",
        },
        {
            "uri": "viking://resources/projects/soil_frontier_genomics/README.md",
            "score": 0.42,
            "abstract": "Soil genomics overview.",
        },
    ]


async def test_only_resources_bucket_is_returned(client, user_with_credential):
    """OV returns memories/skills buckets too; the route exposes only resources."""
    _login(client)
    payload = {
        "total": 1,
        "resources": [{"uri": "viking://resources/projects/a/x.md", "score": 0.5, "abstract": "A"}],
        "memories": [{"uri": "viking://memories/secret", "score": 0.99, "abstract": "hidden"}],
        "skills": [{"uri": "viking://skills/berdl", "score": 0.98, "abstract": "skill"}],
    }
    with patch("app.routes.search.ov_search", AsyncMock(return_value=payload)):
        resp = client.get("/api/search", params={"q": "phage"})

    body = resp.json()
    assert len(body["results"]) == 1
    assert "hidden" not in resp.text


async def test_missing_fields_get_defaults(client, user_with_credential):
    """A result missing score/abstract shouldn't KeyError — defaults fill in."""
    _login(client)
    payload = {"total": 1, "resources": [{"uri": "viking://resources/projects/a/x.md"}]}
    with patch("app.routes.search.ov_search", AsyncMock(return_value=payload)):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 200
    assert resp.json()["results"] == [
        {"uri": "viking://resources/projects/a/x.md", "score": 0.0, "abstract": ""}
    ]


async def test_no_matches_returns_empty_list(client, user_with_credential):
    _login(client)
    with patch(
        "app.routes.search.ov_search", AsyncMock(return_value={"total": 0, "resources": []})
    ):
        resp = client.get("/api/search", params={"q": "nothingmatches"})

    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["results"] == []


async def test_missing_total_falls_back_to_result_count(client, user_with_credential):
    _login(client)
    payload = {"resources": [{"uri": "viking://resources/projects/a/x.md"}]}
    with patch("app.routes.search.ov_search", AsyncMock(return_value=payload)):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.json()["total"] == 1


@pytest.mark.parametrize("payload", [None, {}, {"resources": None}])
async def test_degenerate_ov_payloads_are_handled(client, user_with_credential, payload):
    """OV returning null/empty shouldn't 500 — the route guards each access."""
    _login(client)
    with patch("app.routes.search.ov_search", AsyncMock(return_value=payload)):
        resp = client.get("/api/search", params={"q": "phage"})

    assert resp.status_code == 200
    assert resp.json()["results"] == []
    assert resp.json()["total"] == 0
