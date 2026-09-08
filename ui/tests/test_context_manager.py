"""Tests for the context-manager abstraction layer.

Covers the OpenViking-backed :class:`OpenVikingManager` and the thin
:class:`OpenVikingClient` wrapper around the ``openviking`` SDK. The SDK's
``AsyncHTTPClient`` is patched out throughout, so nothing here needs a live
OpenViking instance.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from cryptography.fernet import Fernet
from openviking_sdk.errors import OpenVikingError as SdkOpenVikingError
from openviking_sdk.errors import UnavailableError

from app.clients.openviking import (
    ADD_RESOURCE_RETRIES,
    OpenVikingClient,
    OpenVikingError,
)
from app.context_manager.base import (
    ContextIngestFile,
    ContextQuery,
    ContextQueryResults,
)
from app.context_manager.openviking import (
    OpenVikingManager,
    OvProvisioningError,
    UnauthenticatedError,
    context_slugify,
    get_user_ov_api_key,
    target_uri,
    user_target_root,
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
# Ingest: slug + URI construction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Acinetobacter ADP1 Explorer", "acinetobacter_adp1_explorer"),
        ("already_a_slug", "already_a_slug"),
        ("Hyphen-Separated Name", "hyphen_separated_name"),
        ("  Padded  Name  ", "padded_name"),
        ("Punctuation!? Removed.", "punctuation_removed"),
        ("!!!", ""),
        ("", ""),
    ],
)
def test_context_slugify(raw, expected):
    assert context_slugify(raw) == expected


def test_user_target_root_keys_on_orcid():
    """Two users' identically-named projects must not share a namespace."""
    a = user_target_root("0000-0001-2345-6789", "shared_name")
    b = user_target_root("0000-0002-9999-9999", "shared_name")

    assert a == "viking://resources/users/0000-0001-2345-6789/shared_name"
    assert a != b


def test_target_uri_preserves_nested_path():
    uri = target_uri("viking://resources/users/orcid/proj", "sub/dir/file.csv")

    assert uri == "viking://resources/users/orcid/proj/sub/dir/file.csv"


@pytest.mark.parametrize("bad", ["../escape.md", "a/../../b.md", "", "/", "./."])
def test_target_uri_rejects_traversal(bad):
    with pytest.raises(ValueError):
        target_uri("viking://resources/users/orcid/proj", bad)


# ---------------------------------------------------------------------------
# OpenVikingManager.insert_file / insert_files
# ---------------------------------------------------------------------------


def _ingest_file(path="notes.md", content=b"hello"):
    return ContextIngestFile(relative_path=path, content=content)


async def test_insert_file_submits_spilled_file(settings, patched_sdk):
    """The file is written to disk and its path handed to add_resource."""
    seen = {}

    async def capture(path, **kwargs):
        seen["path"] = path
        seen["content"] = Path(path).read_bytes()
        seen["kwargs"] = kwargs
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(content=b"file body"), target_root="viking://root/proj"
    )

    assert result.status == "queued"
    assert result.uri == "viking://root/proj/notes.md"
    assert seen["content"] == b"file body"
    # Basename preserved — OV derives the resource's source_name from it.
    assert Path(seen["path"]).name == "notes.md"
    # Never block on indexing inside a request.
    assert seen["kwargs"]["wait"] is False
    assert seen["kwargs"]["to"] == "viking://root/proj/notes.md"


async def test_insert_file_mirrors_nested_path_on_disk(settings, patched_sdk):
    """The spilled path keeps its directories, since OpenViking derives the
    resource's source_name from the path it is handed."""
    seen = {}

    async def capture(path, **kwargs):
        seen["path"] = path
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(path="figures/figure_1.png", content=b"png"),
        target_root="viking://root/proj",
    )

    assert result.uri == "viking://root/proj/figures/figure_1.png"
    # Not flattened to "figure_1.png".
    assert seen["path"].endswith("figures/figure_1.png")


async def test_insert_file_mirrors_deeply_nested_path(settings, patched_sdk):
    seen = {}

    async def capture(path, **kwargs):
        seen["path"] = path
        seen["content"] = Path(path).read_bytes()
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    await manager.insert_file(
        _ingest_file(path="a/b/c/deep.json", content=b"{}"),
        target_root="viking://root/proj",
    )

    assert seen["path"].endswith("a/b/c/deep.json")
    assert seen["content"] == b"{}"


async def test_insert_files_keeps_a_project_tree_intact(settings, patched_sdk):
    """A whole project directory keeps its shape below the root."""
    paths = []

    async def capture(path, **kwargs):
        paths.append(kwargs["to"])
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.insert_files(
        [
            _ingest_file("README.md"),
            _ingest_file("data/data_file_1.json"),
            _ingest_file("figures/figure_1.png"),
        ],
        target_root="viking://resources/users/orcid/ingest_smoke_test",
    )

    assert out.queued == 3
    assert paths == [
        "viking://resources/users/orcid/ingest_smoke_test/README.md",
        "viking://resources/users/orcid/ingest_smoke_test/data/data_file_1.json",
        "viking://resources/users/orcid/ingest_smoke_test/figures/figure_1.png",
    ]


async def test_insert_file_rejects_absolute_path_at_spill(settings, patched_sdk):
    """An absolute path must not escape the temp directory."""
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(path="/etc/passwd"), target_root="viking://root/proj"
    )

    assert result.status == "failed"
    patched_sdk.add_resource.assert_not_awaited()


async def test_insert_file_cleans_up_temp_file(settings, patched_sdk):
    spilled = {}

    async def capture(path, **kwargs):
        spilled["path"] = path
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    await manager.insert_file(_ingest_file(), target_root="viking://root/proj")

    assert not Path(spilled["path"]).exists()


async def test_insert_file_cleans_up_temp_file_on_failure(settings, patched_sdk):
    """A failed submission must not leak the spilled file."""
    spilled = {}

    async def boom(path, **kwargs):
        spilled["path"] = path
        raise SdkOpenVikingError("rejected")

    patched_sdk.add_resource = AsyncMock(side_effect=boom)
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(), target_root="viking://root/proj"
    )

    assert result.status == "failed"
    assert not Path(spilled["path"]).exists()


async def test_insert_file_handles_binary_content(settings, patched_sdk):
    """Binary files ingest byte-for-byte — no text decoding anywhere."""
    blob = bytes(range(256))
    seen = {}

    async def capture(path, **kwargs):
        seen["content"] = Path(path).read_bytes()
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(path="fig.png", content=blob), target_root="viking://root/proj"
    )

    assert result.status == "queued"
    assert seen["content"] == blob


async def test_insert_file_reports_unsafe_path_without_calling_backend(
    settings, patched_sdk
):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(path="../escape.md"), target_root="viking://root/proj"
    )

    assert result.status == "failed"
    assert result.uri is None
    patched_sdk.add_resource.assert_not_awaited()


async def test_insert_file_closes_the_client(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    await manager.insert_file(_ingest_file(), target_root="viking://root/proj")

    patched_sdk.close.assert_awaited_once()


async def test_insert_files_batches_and_counts(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.insert_files(
        [_ingest_file("a.md"), _ingest_file("b/c.md")],
        target_root="viking://root/proj",
    )

    assert out.queued == 2
    assert out.failed == 0
    assert [r.uri for r in out.results] == [
        "viking://root/proj/a.md",
        "viking://root/proj/b/c.md",
    ]


async def test_insert_files_continues_past_a_failure(settings, patched_sdk):
    """One rejected file must not abort the rest of the batch."""

    async def fail_second(path, **kwargs):
        if kwargs["to"].endswith("b.md"):
            raise SdkOpenVikingError("rejected")
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=fail_second)
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.insert_files(
        [_ingest_file("a.md"), _ingest_file("b.md"), _ingest_file("c.md")],
        target_root="viking://root/proj",
    )

    assert out.queued == 2
    assert out.failed == 1
    assert [r.status for r in out.results] == ["queued", "failed", "queued"]


async def test_insert_files_reuses_one_client(settings, patched_sdk):
    """A batch opens and closes exactly one client, not one per file."""
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    await manager.insert_files(
        [_ingest_file(f"f{i}.md") for i in range(4)],
        target_root="viking://root/proj",
    )

    patched_sdk.initialize.assert_awaited_once()
    patched_sdk.close.assert_awaited_once()


async def test_insert_files_closes_client_when_a_file_fails(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(side_effect=SdkOpenVikingError("nope"))
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.insert_files(
        [_ingest_file()], target_root="viking://root/proj"
    )

    assert out.failed == 1
    patched_sdk.close.assert_awaited_once()


async def test_insert_files_empty_batch_skips_the_backend(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.insert_files([], target_root="viking://root/proj")

    assert (out.queued, out.failed, out.results) == (0, 0, [])
    patched_sdk.initialize.assert_not_awaited()


async def test_insert_file_reports_transport_failure(settings, patched_sdk):
    """An unreachable backend is a per-file failure, not an exception."""
    patched_sdk.add_resource = AsyncMock(side_effect=httpx.ConnectError("down"))
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(), target_root="viking://root/proj"
    )

    assert result.status == "failed"
    # The reason is generic — it must not name the backend.
    assert "openviking" not in (result.reason or "").lower()


async def test_insert_file_propagates_unexpected_errors(settings, patched_sdk):
    """A bug in our own code must surface, not be reported as a bad file."""
    patched_sdk.add_resource = AsyncMock(side_effect=TypeError("bug"))
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(TypeError):
        await manager.insert_file(_ingest_file(), target_root="viking://root/proj")


async def test_insert_file_captures_task_id(settings, patched_sdk):
    """The submission's task id is kept so the ingest stays pollable."""
    patched_sdk.add_resource = AsyncMock(
        return_value={"status": "success", "task_id": "task-abc"}
    )
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(), target_root="viking://root/proj"
    )

    assert result.task_id == "task-abc"


async def test_insert_file_tolerates_missing_task_id(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_file(
        _ingest_file(), target_root="viking://root/proj"
    )

    assert result.status == "queued"
    assert result.task_id is None


# ---------------------------------------------------------------------------
# OpenVikingManager.task_statuses
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ov_status,expected",
    [
        ("pending", "queued"),
        ("running", "processing"),
        # No cancel is exposed, so a cancelling task still reads as in-flight.
        ("cancelling", "processing"),
        ("completed", "completed"),
        ("failed", "failed"),
        # The file did not land, so a cancelled task is a failure to the user.
        ("cancelled", "failed"),
        ("something-new", "unknown"),
    ],
)
async def test_task_statuses_maps_backend_states(
    settings, patched_sdk, ov_status, expected
):
    patched_sdk.get_task = AsyncMock(return_value={"status": ov_status})
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.task_statuses(["t1"])

    assert out["t1"][0] == expected


async def test_task_statuses_reports_expired_task_as_unknown(settings, patched_sdk):
    """An expired record is not proof of failure — say we don't know."""
    patched_sdk.get_task = AsyncMock(return_value=None)
    manager = OpenVikingManager(settings, "user-key")

    assert (await manager.task_statuses(["t1"]))["t1"] == ("unknown", None)


async def test_task_statuses_returns_error_detail(settings, patched_sdk):
    patched_sdk.get_task = AsyncMock(
        return_value={"status": "failed", "error": "parse blew up"}
    )
    manager = OpenVikingManager(settings, "user-key")

    assert (await manager.task_statuses(["t1"]))["t1"] == ("failed", "parse blew up")


async def test_task_statuses_survives_backend_failure(settings, patched_sdk):
    """A poll must never raise — the caller falls back to last-known status."""
    patched_sdk.get_task = AsyncMock(side_effect=httpx.ConnectError("down"))
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.task_statuses(["t1", "t2"])

    assert out == {"t1": ("unknown", None), "t2": ("unknown", None)}


async def test_task_statuses_handles_mixed_results(settings, patched_sdk):
    async def per_task(task_id):
        if task_id == "t2":
            raise httpx.ConnectError("down")
        return {"status": "completed"}

    patched_sdk.get_task = AsyncMock(side_effect=per_task)
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.task_statuses(["t1", "t2", "t3"])

    assert out["t1"][0] == "completed"
    assert out["t2"][0] == "unknown"
    assert out["t3"][0] == "completed"


async def test_task_statuses_empty_skips_the_backend(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.task_statuses([]) == {}
    patched_sdk.initialize.assert_not_awaited()


async def test_task_statuses_closes_the_client(settings, patched_sdk):
    patched_sdk.get_task = AsyncMock(return_value={"status": "completed"})
    manager = OpenVikingManager(settings, "user-key")

    await manager.task_statuses(["t1"])

    patched_sdk.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# OpenVikingClient.add_resource retries
# ---------------------------------------------------------------------------


async def test_add_resource_retries_transient_error(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(
        side_effect=[UnavailableError("busy"), {"ok": True}]
    )
    client = await OpenVikingClient.create("user-key")

    with patch("app.clients.openviking.asyncio.sleep", AsyncMock()) as sleep:
        result = await client.add_resource("/tmp/f.md", "viking://x/f.md", reason="r")

    assert result == {"ok": True}
    assert patched_sdk.add_resource.await_count == 2
    sleep.assert_awaited_once()


async def test_add_resource_gives_up_after_retry_cap(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(side_effect=UnavailableError("busy"))
    client = await OpenVikingClient.create("user-key")

    with patch("app.clients.openviking.asyncio.sleep", AsyncMock()):
        with pytest.raises(UnavailableError):
            await client.add_resource("/tmp/f.md", "viking://x/f.md", reason="r")

    assert patched_sdk.add_resource.await_count == ADD_RESOURCE_RETRIES


async def test_add_resource_does_not_retry_other_errors(settings, patched_sdk):
    """A non-transient error fails immediately rather than burning the budget."""
    patched_sdk.add_resource = AsyncMock(side_effect=SdkOpenVikingError("bad input"))
    client = await OpenVikingClient.create("user-key")

    with pytest.raises(SdkOpenVikingError):
        await client.add_resource("/tmp/f.md", "viking://x/f.md", reason="r")

    assert patched_sdk.add_resource.await_count == 1


# ---------------------------------------------------------------------------
# ContextQuery model defaults
# ---------------------------------------------------------------------------


def test_context_query_defaults():
    q = ContextQuery(query="hello")

    assert q.root_path is None
    assert q.limit == 10
    assert q.score_threshold is None
