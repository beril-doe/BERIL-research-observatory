"""Tests for the context-manager abstraction layer.

Covers the OpenViking-backed :class:`OpenVikingManager` and the thin
:class:`OpenVikingClient` wrapper around the ``openviking`` SDK. The SDK's
``AsyncHTTPClient`` is patched out throughout, so nothing here needs a live
OpenViking instance.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from app.clients.openviking import OpenVikingClient, OpenVikingError
from app.context_manager.base import ContextQuery, ContextQueryResults
from app.context_manager.openviking import (
    OpenVikingManager,
    OvProvisioningError,
    UnauthenticatedError,
    get_user_ov_api_key,
)
from app.crypto import decrypt_secret, encrypt_secret
from app.db.crud import get_ov_credential
from app.db.models import BerilUser, OvUserCredential

_CREDENTIAL_KEY = Fernet.generate_key().decode()

_ENV = {
    "BERIL_OV_URL": "http://ov.test:1933",
    "BERIL_OV_ACCOUNT_ID": "beril",
    "BERIL_OV_ADMIN_KEY": "admin-key",
    "BERIL_OV_CREDENTIAL_KEY": _CREDENTIAL_KEY,
    "BERIL_SESSION_SECRET_KEY": "test-session-secret",
}

# A representative OpenViking ``find`` payload. Note the manager reads the
# ``abstract`` field into ``QueryResult.text``.
FIND_PAYLOAD = {
    "resources": [
        {
            "uri": "viking://resources/projects/alpha.md",
            "context_type": "document",
            "score": 0.93,
            "abstract": "Alpha project overview.",
        },
        {
            "uri": "viking://resources/projects/beta.md",
            "context_type": "document",
            "score": 0.41,
            "abstract": "Beta project overview.",
        },
    ]
}


@pytest.fixture
def settings():
    """Real Settings object built from the test environment."""
    with patch.dict(os.environ, _ENV):
        import app.config as cfg

        cfg._settings = None
        yield cfg.get_settings()
        cfg._settings = None


@pytest.fixture
def sdk_client():
    """A stand-in for ``openviking.AsyncHTTPClient``.

    ``initialize``/``close``/``find``/``ls`` are all async on the real SDK, so
    they are ``AsyncMock`` here — that is what makes an un-awaited ``close()``
    detectable.
    """
    inst = MagicMock()
    inst.initialize = AsyncMock(return_value=None)
    inst.close = AsyncMock(return_value=None)
    inst.find = AsyncMock(return_value=FIND_PAYLOAD)
    inst.ls = AsyncMock(return_value=["alpha.md", "beta.md"])
    return inst


@pytest.fixture
def patched_sdk(sdk_client):
    """Patch the SDK class the client module imported, yielding the instance."""
    with patch("app.clients.openviking.AsyncHTTPClient", return_value=sdk_client):
        yield sdk_client


# ---------------------------------------------------------------------------
# OpenVikingClient
# ---------------------------------------------------------------------------


async def test_create_initializes_underlying_client(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key", base_url="http://ov.test:1933")

    patched_sdk.initialize.assert_awaited_once()
    assert isinstance(client, OpenVikingClient)


async def test_client_defaults_base_url_to_settings(settings, sdk_client):
    """Omitting base_url falls back to ``settings.ov_url``."""
    with patch(
        "app.clients.openviking.AsyncHTTPClient", return_value=sdk_client
    ) as sdk_cls:
        await OpenVikingClient.create("user-key")

    assert sdk_cls.call_args.kwargs["url"] == settings.ov_url
    assert sdk_cls.call_args.kwargs["api_key"] == "user-key"


async def test_find_passes_through_query_parameters(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key")
    await client.find("some query", target_uri="viking://x", limit=3)

    patched_sdk.find.assert_awaited_once_with(
        "some query", limit=3, target_uri="viking://x", options=None
    )


async def test_find_omits_options_when_no_score_threshold(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key")
    await client.find("q")

    assert patched_sdk.find.await_args.kwargs["options"] is None


async def test_find_wraps_score_threshold_in_options(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key")
    await client.find("q", score_threshold=0.75)

    assert patched_sdk.find.await_args.kwargs["options"] == {"score_threshold": 0.75}


async def test_list_files_prefixes_viking_scheme(settings, patched_sdk):
    """``list_files`` takes a bare path and builds the ``viking://`` URI."""
    client = await OpenVikingClient.create("user-key")
    await client.list_files("resources/projects")

    patched_sdk.ls.assert_awaited_once_with("viking://resources/projects")


async def test_close_closes_underlying_client(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key")
    await client.close()

    patched_sdk.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# OpenVikingManager.query
# ---------------------------------------------------------------------------


async def test_query_maps_payload_into_results(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha"))

    assert isinstance(out, ContextQueryResults)
    assert out.query == "alpha"
    assert [r.uri for r in out.results] == [
        "viking://resources/projects/alpha.md",
        "viking://resources/projects/beta.md",
    ]
    # ``abstract`` from the payload lands in ``text``.
    assert out.results[0].text == "Alpha project overview."
    assert out.results[0].score == 0.93
    assert out.results[0].context_type == "document"


async def test_query_forwards_all_query_fields(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(
        ContextQuery(
            query="alpha",
            root_path="viking://resources/projects",
            limit=5,
            score_threshold=0.5,
        )
    )

    patched_sdk.find.assert_awaited_once_with(
        "alpha",
        limit=5,
        target_uri="viking://resources/projects",
        options={"score_threshold": 0.5},
    )


async def test_query_handles_empty_resources(settings, patched_sdk):
    patched_sdk.find.return_value = {"resources": []}
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.query(ContextQuery(query="nothing"))

    assert out.results == []
    assert out.query == "nothing"


async def test_query_handles_missing_resources_key(settings, patched_sdk):
    """A payload with no ``resources`` key degrades to an empty result set."""
    patched_sdk.find.return_value = {}
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.query(ContextQuery(query="nothing"))

    assert out.results == []


async def test_query_uses_the_credentialed_api_key(settings, sdk_client):
    """The manager's api_key is handed to the SDK, not the admin key."""
    with patch(
        "app.clients.openviking.AsyncHTTPClient", return_value=sdk_client
    ) as sdk_cls:
        await OpenVikingManager(settings, "per-user-key").query(ContextQuery(query="q"))

    assert sdk_cls.call_args.kwargs["api_key"] == "per-user-key"


async def test_query_closes_the_client(settings, patched_sdk):
    """Regression: the per-call client must be closed, or connections leak.

    ``AsyncHTTPClient.close`` is a coroutine, so calling it without ``await``
    leaves it un-awaited and the connection open.
    """
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(ContextQuery(query="alpha"))

    patched_sdk.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# OpenVikingManager.list_files
# ---------------------------------------------------------------------------


async def test_list_files_queries_the_projects_root(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.list_files()

    patched_sdk.ls.assert_awaited_once_with("viking://resources/projects")
    assert out == ["alpha.md", "beta.md"]


async def test_list_files_closes_the_client(settings, patched_sdk):
    """Regression: same un-awaited ``close()`` leak as in ``query``."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.list_files()

    patched_sdk.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_user_ov_api_key
# ---------------------------------------------------------------------------


@pytest.fixture
async def ov_user(db_session):
    u = BerilUser(orcid_id="0000-0001-2345-6789", display_name="Alice Researcher")
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


def _already_exists() -> OpenVikingError:
    return OpenVikingError("exists", status_code=409, code="ALREADY_EXISTS")


async def test_get_key_requires_a_user(settings, db_session):
    with pytest.raises(UnauthenticatedError):
        await get_user_ov_api_key(db_session, None)


async def test_get_key_requires_a_persisted_user(settings, db_session):
    """A BerilUser that was never committed has no id — treat as unauthenticated."""
    with pytest.raises(UnauthenticatedError):
        await get_user_ov_api_key(db_session, BerilUser(orcid_id="0000-0001-2345-6789"))


async def test_get_key_returns_decrypted_stored_key(settings, db_session, ov_user):
    db_session.add(
        OvUserCredential(
            user_id=ov_user.id,
            account_id="beril",
            ov_user_id=ov_user.orcid_id,
            encrypted_key=encrypt_secret("stored-key", _CREDENTIAL_KEY),
        )
    )
    await db_session.commit()

    with patch("app.context_manager.openviking.register_ov_user") as register:
        key = await get_user_ov_api_key(db_session, ov_user)

    assert key == "stored-key"
    # An existing credential must never trigger an upstream call.
    register.assert_not_called()


async def test_get_key_provisions_and_stores_on_first_use(settings, db_session, ov_user):
    register = AsyncMock(return_value={"user_key": "minted-key"})
    with patch("app.context_manager.openviking.register_ov_user", register):
        key = await get_user_ov_api_key(db_session, ov_user)

    assert key == "minted-key"
    register.assert_awaited_once_with(ov_user.orcid_id)

    cred = await get_ov_credential(db_session, ov_user.id)
    assert cred is not None
    assert cred.ov_user_id == ov_user.orcid_id
    assert cred.account_id == "beril"
    # Persisted encrypted, but round-trips to the plaintext we returned.
    assert cred.encrypted_key != "minted-key"
    assert decrypt_secret(cred.encrypted_key, _CREDENTIAL_KEY) == "minted-key"


async def test_get_key_regenerates_when_ov_user_exists_without_key(
    settings, db_session, ov_user
):
    """The 409 case resolves silently — the user never sees an OV conflict."""
    register = AsyncMock(side_effect=_already_exists())
    regenerate = AsyncMock(return_value={"user_key": "regen-key"})
    with patch("app.context_manager.openviking.register_ov_user", register), patch(
        "app.context_manager.openviking.regenerate_ov_user_key", regenerate
    ):
        key = await get_user_ov_api_key(db_session, ov_user)

    assert key == "regen-key"
    regenerate.assert_awaited_once_with(ov_user.orcid_id)

    cred = await get_ov_credential(db_session, ov_user.id)
    assert decrypt_secret(cred.encrypted_key, _CREDENTIAL_KEY) == "regen-key"


async def test_get_key_regenerates_on_bare_already_exists_code(
    settings, db_session, ov_user
):
    """OV signals the conflict by code even when the status isn't 409."""
    register = AsyncMock(
        side_effect=OpenVikingError("exists", code="ALREADY_EXISTS")
    )
    regenerate = AsyncMock(return_value={"user_key": "regen-key"})
    with patch("app.context_manager.openviking.register_ov_user", register), patch(
        "app.context_manager.openviking.regenerate_ov_user_key", regenerate
    ):
        assert await get_user_ov_api_key(db_session, ov_user) == "regen-key"


async def test_get_key_raises_when_registration_fails(settings, db_session, ov_user):
    register = AsyncMock(
        side_effect=OpenVikingError("boom", status_code=500, code="INTERNAL")
    )
    with patch("app.context_manager.openviking.register_ov_user", register):
        with pytest.raises(OvProvisioningError):
            await get_user_ov_api_key(db_session, ov_user)

    assert await get_ov_credential(db_session, ov_user.id) is None


async def test_get_key_raises_when_regeneration_fails(settings, db_session, ov_user):
    """A conflict we then can't recover from is a real upstream fault."""
    register = AsyncMock(side_effect=_already_exists())
    regenerate = AsyncMock(side_effect=OpenVikingError("nope", status_code=502))
    with patch("app.context_manager.openviking.register_ov_user", register), patch(
        "app.context_manager.openviking.regenerate_ov_user_key", regenerate
    ):
        with pytest.raises(OvProvisioningError):
            await get_user_ov_api_key(db_session, ov_user)


async def test_get_key_raises_when_no_key_returned(settings, db_session, ov_user):
    """A success envelope without a ``user_key`` is unusable."""
    register = AsyncMock(return_value={"user_id": "someone"})
    with patch("app.context_manager.openviking.register_ov_user", register):
        with pytest.raises(OvProvisioningError):
            await get_user_ov_api_key(db_session, ov_user)

    assert await get_ov_credential(db_session, ov_user.id) is None


# ---------------------------------------------------------------------------
# ContextQuery model defaults
# ---------------------------------------------------------------------------


def test_context_query_defaults():
    q = ContextQuery(query="hello")

    assert q.root_path is None
    assert q.limit == 10
    assert q.score_threshold is None
