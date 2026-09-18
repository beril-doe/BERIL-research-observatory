"""Tests for the Langfuse ingestion relay (``/lf/api/public/...``).

The upstream httpx client is patched so nothing reaches Langfuse Cloud. What
matters: the relay rejects anything but a valid BERIL PAT, exposes only the
SDK's write paths, and forwards with the server-held keypair rather than
whatever the client sent.
"""

from __future__ import annotations

import base64
import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.db.crud import get_or_create_api_token
from app.db.models import BerilUser
from app.db.session import get_db
from app.main import create_app

_ENV = {
    "BERIL_TEST_SKIP_LIFESPAN": "True",
    "BERIL_SESSION_SECRET_KEY": "test-session-secret",
    "BERIL_LANGFUSE_PUBLIC_KEY": "pk-lf-server",
    "BERIL_LANGFUSE_SECRET_KEY": "sk-lf-server",
    "BERIL_LANGFUSE_BASE_URL": "https://langfuse.test/",
}


def _basic(username: str, password: str) -> dict[str, str]:
    return {"Authorization": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()}


def _make_client(db_session, repository_data, app_data_context, env: dict[str, str]):
    import app.config as cfg

    cfg._settings = None
    app_instance = create_app()

    async def override_get_db() -> AsyncGenerator:
        yield db_session

    app_instance.dependency_overrides[get_db] = override_get_db
    c = TestClient(app_instance, raise_server_exceptions=True)
    c.__enter__()
    app_instance.state.repo_data = repository_data
    app_instance.state.base_context = app_data_context
    return c


@pytest.fixture
def client(repository_data, app_data_context, db_session):
    with patch.dict(os.environ, _ENV):
        c = _make_client(db_session, repository_data, app_data_context, _ENV)
        yield c
        c.__exit__(None, None, None)
        import app.config as cfg

        cfg._settings = None


@pytest.fixture
async def pat(db_session) -> str:
    u = BerilUser(orcid_id="0000-0001-2345-6789", display_name="Alice Researcher")
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    raw, _ = await get_or_create_api_token(db_session, u.id)
    return raw


def _patch_upstream(status_code: int = 200, body: bytes = b'{"ok":true}'):
    """Patch httpx.AsyncClient so ``request`` records the call and returns a canned response."""
    response = httpx.Response(status_code, content=body, headers={"content-type": "application/json"})
    instance = MagicMock()
    instance.request = AsyncMock(return_value=response)
    instance.__aenter__ = AsyncMock(return_value=instance)
    instance.__aexit__ = AsyncMock(return_value=False)
    return patch("app.routes.langfuse.httpx.AsyncClient", MagicMock(return_value=instance)), instance


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_no_auth_is_401(client):
    assert client.post("/lf/api/public/otel/v1/traces", content=b"x").status_code == 401


def test_bad_pat_is_401(client):
    resp = client.post("/lf/api/public/otel/v1/traces", content=b"x", headers=_basic("beril", "nope"))
    assert resp.status_code == 401


def test_malformed_basic_is_401(client):
    resp = client.post("/lf/api/public/otel/v1/traces", headers={"Authorization": "Basic !!!"})
    assert resp.status_code == 401


async def test_bearer_is_not_accepted(client, pat):
    # The SDK never sends Bearer; keep the relay's accepted shapes minimal.
    resp = client.post("/lf/api/public/otel/v1/traces", headers={"Authorization": f"Bearer {pat}"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Write-only surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/lf/api/public/traces"),
        ("GET", "/lf/api/public/observations"),
        ("DELETE", "/lf/api/public/traces/abc"),
        ("GET", "/lf/api/public/media/abc"),
        ("POST", "/lf/api/public/ingestion"),
        ("POST", "/lf/api/public/scores"),
    ],
)
async def test_non_write_paths_are_not_exposed(client, pat, method, path):
    resp = client.request(method, path, headers=_basic("beril", pat))
    assert resp.status_code in (404, 405)


# ---------------------------------------------------------------------------
# Forwarding
# ---------------------------------------------------------------------------


async def test_traces_forwarded_with_server_keys(client, pat):
    patcher, instance = _patch_upstream(207, b"partial")
    with patcher:
        resp = client.post(
            "/lf/api/public/otel/v1/traces",
            content=b"\x0a\x00",
            headers={
                **_basic("beril", pat),
                "Content-Type": "application/x-protobuf",
                "Content-Encoding": "gzip",
                "x-langfuse-sdk-name": "python",
                "x-langfuse-public-key": "beril",
                "User-Agent": "beril-langfuse-hook",
            },
        )

    assert resp.status_code == 207
    assert resp.content == b"partial"
    instance.request.assert_awaited_once()
    args, kwargs = instance.request.call_args
    assert args == ("POST", "https://langfuse.test/api/public/otel/v1/traces")
    assert kwargs["content"] == b"\x0a\x00"
    assert kwargs["auth"] == ("pk-lf-server", "sk-lf-server")
    sent = {k.lower(): v for k, v in kwargs["headers"].items()}
    assert sent["content-type"] == "application/x-protobuf"
    assert sent["content-encoding"] == "gzip"
    assert sent["x-langfuse-sdk-name"] == "python"
    assert sent["x-langfuse-public-key"] == "pk-lf-server"
    # The client's own credential and UA never reach Langfuse.
    assert "authorization" not in sent
    assert "user-agent" not in sent


async def test_media_paths_forwarded(client, pat):
    patcher, instance = _patch_upstream()
    with patcher:
        assert client.post("/lf/api/public/media", json={"a": 1}, headers=_basic("beril", pat)).status_code == 200
        assert client.patch("/lf/api/public/media/m-1", json={"b": 2}, headers=_basic("beril", pat)).status_code == 200
    calls = [c.args for c in instance.request.await_args_list]
    assert calls == [
        ("POST", "https://langfuse.test/api/public/media"),
        ("PATCH", "https://langfuse.test/api/public/media/m-1"),
    ]


async def test_upstream_unreachable_is_502(client, pat):
    patcher, instance = _patch_upstream()
    instance.request = AsyncMock(side_effect=httpx.ConnectError("down"))
    with patcher:
        resp = client.post("/lf/api/public/otel/v1/traces", content=b"x", headers=_basic("beril", pat))
    assert resp.status_code == 502


async def test_unconfigured_relay_is_503(repository_data, app_data_context, db_session):
    env = {k: v for k, v in _ENV.items() if not k.startswith("BERIL_LANGFUSE_")}
    with patch.dict(os.environ, env, clear=False):
        for k in ("BERIL_LANGFUSE_PUBLIC_KEY", "BERIL_LANGFUSE_SECRET_KEY"):
            os.environ.pop(k, None)
        c = _make_client(db_session, repository_data, app_data_context, env)
        try:
            u = BerilUser(orcid_id="0000-0002-0000-0000", display_name="Bob")
            db_session.add(u)
            await db_session.commit()
            await db_session.refresh(u)
            raw, _ = await get_or_create_api_token(db_session, u.id)
            resp = c.post("/lf/api/public/otel/v1/traces", content=b"x", headers=_basic("beril", raw))
            assert resp.status_code == 503
        finally:
            c.__exit__(None, None, None)
            import app.config as cfg

            cfg._settings = None
