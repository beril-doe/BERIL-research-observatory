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
    HOUSE_ACCOUNT_ID,
    OpenVikingManager,
    OvProvisioningError,
    ReservedNamespaceError,
    UnauthenticatedError,
    _collapse_fragments,
    _grep_nodes,
    context_slugify,
    corpus_root,
    get_user_ov_api_key,
    is_synthetic_node,
    listing_uri,
    source_document,
    target_uri,
    user_namespace_root,
    user_target_root,
)
from app.crypto import decrypt_secret, encrypt_secret
from app.db.crud import get_ov_credential
from app.db.models import BerilUser, OvUserCredential
from cryptography.fernet import Fernet
from openviking_sdk.errors import OpenVikingError as SdkOpenVikingError
from openviking_sdk.errors import UnavailableError

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

    ``initialize``/``close``/``find``/``ls``/``grep`` are all async on the real
    SDK, so they are ``AsyncMock`` here — that is what makes an un-awaited
    ``close()`` detectable.
    """
    inst = MagicMock()
    inst.initialize = AsyncMock(return_value=None)
    inst.close = AsyncMock(return_value=None)
    inst.find = AsyncMock(return_value=FIND_PAYLOAD)
    inst.ls = AsyncMock(return_value=["alpha.md", "beta.md"])
    inst.grep = AsyncMock(return_value={"matches": [], "total": 0})
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


async def test_list_files_passes_the_uri_through(settings, patched_sdk):
    """``list_files`` takes a full URI — callers resolve the target themselves.

    Scoping happens above this layer (see ``listing_uri``), so prepending a
    scheme here would mean parsing it back off again.
    """
    client = await OpenVikingClient.create("user-key")
    await client.list_files("viking://resources/users/0000-1/alpha")

    patched_sdk.ls.assert_awaited_once_with(
        "viking://resources/users/0000-1/alpha", recursive=False, simple=False
    )


async def test_list_files_forwards_listing_options(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key")
    await client.list_files(
        "viking://x", recursive=True, simple=True, node_limit=25
    )

    patched_sdk.ls.assert_awaited_once_with(
        "viking://x", recursive=True, simple=True, node_limit=25
    )


async def test_list_files_omits_an_unset_node_limit(settings, patched_sdk):
    """An unset node_limit leaves the backend's own default in place."""
    client = await OpenVikingClient.create("user-key")
    await client.list_files("viking://x")

    assert "node_limit" not in patched_sdk.ls.await_args.kwargs


async def test_client_grep_passes_uri_pattern_and_options(settings, patched_sdk):
    client = await OpenVikingClient.create("user-key")
    await client.grep(
        "viking://x", "pat", case_insensitive=True, exclude_uri="viking://x/s",
        node_limit=9,
    )

    patched_sdk.grep.assert_awaited_once_with(
        "viking://x", "pat", case_insensitive=True,
        exclude_uri="viking://x/s", node_limit=9,
    )


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


async def test_query_forwards_the_extended_options(settings, patched_sdk):
    """Filter, time bounds, node limit and read_content all reach the backend."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(
        ContextQuery(
            query="alpha",
            root_path="viking://resources/projects",
            limit=5,
            score_threshold=0.5,
            filter={"op": "must", "field": "uri", "conds": ["viking://x/"]},
            since="7d",
            until="2026-01-01",
            time_field="created_at",
            node_limit=50,
            read_content=True,
        )
    )

    assert patched_sdk.find.await_args.kwargs["options"] == {
        "score_threshold": 0.5,
        "filter": {"op": "must", "field": "uri", "conds": ["viking://x/"]},
        "since": "7d",
        "until": "2026-01-01",
        "time_field": "created_at",
        "node_limit": 50,
        "read_content": True,
    }


async def test_query_omits_unset_options(settings, patched_sdk):
    """An unset option is absent, not None.

    Sending ``None`` would override the backend's own default with a value the
    caller never chose.
    """
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(ContextQuery(query="alpha"))

    assert patched_sdk.find.await_args.kwargs["options"] is None


async def test_query_omits_read_content_when_false(settings, patched_sdk):
    """``read_content=False`` is the default, so it is not sent at all."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(ContextQuery(query="alpha", read_content=False))

    assert patched_sdk.find.await_args.kwargs["options"] is None


async def test_query_maps_match_reason_and_content(settings, patched_sdk):
    patched_sdk.find.return_value = {
        "resources": [
            {
                "uri": "viking://x/a.md",
                "context_type": "document",
                "score": 0.8,
                "abstract": "a summary",
                "match_reason": "matched on title",
                "content": "the whole document",
            }
        ],
        "total": 1,
    }
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha", read_content=True))

    assert out.results[0].match_reason == "matched on title"
    assert out.results[0].content == "the whole document"
    # The abstract stays in ``text`` — content is the document, not a summary.
    assert out.results[0].text == "a summary"


async def test_query_reports_backend_total_over_row_count(settings, patched_sdk):
    """A limited query still reports how many the backend found."""
    patched_sdk.find.return_value = {
        "resources": [
            {"uri": "viking://x/a.md", "context_type": "d", "score": 1.0,
             "abstract": "a"}
        ],
        "total": 97,
    }
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha", limit=1))

    assert out.total == 97
    assert len(out.results) == 1


async def test_query_falls_back_to_row_count_without_a_total(settings, patched_sdk):
    patched_sdk.find.return_value = {
        "resources": [
            {"uri": "viking://x/a.md", "context_type": "d", "score": 1.0,
             "abstract": "a"},
            {"uri": "viking://x/b.md", "context_type": "d", "score": 0.9,
             "abstract": "b"},
        ]
    }
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha"))

    assert out.total == 2


async def test_query_tolerates_missing_fields_in_a_hit(settings, patched_sdk):
    """A hit missing uri/score/abstract maps to empty values, not a 500."""
    patched_sdk.find.return_value = {"resources": [{}]}
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha"))

    r = out.results[0]
    assert (r.uri, r.context_type, r.score, r.text) == ("", "", 0.0, "")


async def test_query_closes_the_client_when_find_raises(settings, patched_sdk):
    """A failed query must not leak the connection."""
    patched_sdk.find.side_effect = UnavailableError("backend down")
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(UnavailableError):
        await manager.query(ContextQuery(query="alpha"))

    patched_sdk.close.assert_awaited_once()


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


async def test_list_files_lists_the_given_uri(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.list_files("viking://resources/users/0000-1/alpha")

    patched_sdk.ls.assert_awaited_once_with(
        "viking://resources/users/0000-1/alpha", recursive=False, simple=False
    )
    assert out == ["alpha.md", "beta.md"]


async def test_list_files_returns_empty_for_an_unknown_path(settings, patched_sdk):
    """An un-ingested project is empty, not an error."""
    patched_sdk.ls.return_value = None
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.list_files("viking://x/never-ingested") == []


async def test_list_files_closes_the_client(settings, patched_sdk):
    """Regression: same un-awaited ``close()`` leak as in ``query``."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.list_files("viking://x")

    patched_sdk.close.assert_awaited_once()


async def test_list_files_closes_the_client_when_ls_raises(settings, patched_sdk):
    patched_sdk.ls.side_effect = UnavailableError("backend down")
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(UnavailableError):
        await manager.list_files("viking://x")

    patched_sdk.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# OpenVikingManager.grep
# ---------------------------------------------------------------------------


async def test_grep_passes_uri_and_pattern(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.grep("viking://resources/users/0000-1", "metal binding")

    patched_sdk.grep.assert_awaited_once_with(
        "viking://resources/users/0000-1",
        "metal binding",
        case_insensitive=False,
    )
    assert out == {"matches": [], "total": 0}


async def test_grep_forwards_options(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    await manager.grep(
        "viking://x",
        "pat",
        case_insensitive=True,
        exclude_uri="viking://x/skip",
        node_limit=25,
    )

    patched_sdk.grep.assert_awaited_once_with(
        "viking://x",
        "pat",
        case_insensitive=True,
        exclude_uri="viking://x/skip",
        node_limit=25,
    )


async def test_grep_omits_unset_options(settings, patched_sdk):
    """Unset options leave the backend's own defaults in place."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.grep("viking://x", "pat")

    kwargs = patched_sdk.grep.await_args.kwargs
    assert "exclude_uri" not in kwargs
    assert "node_limit" not in kwargs


async def test_grep_returns_empty_dict_for_no_payload(settings, patched_sdk):
    patched_sdk.grep.return_value = None
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.grep("viking://x", "pat") == {}


async def test_grep_closes_the_client(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    await manager.grep("viking://x", "pat")

    patched_sdk.close.assert_awaited_once()


async def test_grep_closes_the_client_when_grep_raises(settings, patched_sdk):
    patched_sdk.grep.side_effect = UnavailableError("backend down")
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(UnavailableError):
        await manager.grep("viking://x", "pat")

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


def test_user_namespace_root_is_the_whole_user():
    assert user_namespace_root("0000-1") == "viking://resources/users/0000-1"


def test_corpus_root_is_every_owner():
    assert corpus_root() == "viking://resources/users"


def test_listing_uri_resolves_at_every_depth():
    assert listing_uri() == "viking://resources/users"
    assert listing_uri("0000-1") == "viking://resources/users/0000-1"
    assert listing_uri("0000-1", "alpha") == "viking://resources/users/0000-1/alpha"
    assert (
        listing_uri("0000-1", "alpha", "memories/pitfalls.md")
        == "viking://resources/users/0000-1/alpha/memories/pitfalls.md"
    )


def test_listing_uri_reads_any_owner():
    """Reads are global: the owner narrows the target, it does not authorize it.

    A submitted project is owned by one user and readable by everyone, so
    addressing another owner is the normal case, not an attack.
    """
    assert listing_uri("0000-2", "alpha") == "viking://resources/users/0000-2/alpha"


def test_listing_uri_boundary_is_the_corpus_not_the_owner():
    """Traversal may not climb out of ``resources/users/``.

    The owner is no longer the boundary — reads span owners — but the corpus
    root still is, so a path cannot reach the wider resource tree.
    """
    for attack in ["../../docs", "../..", "..", "a/../../../projects"]:
        with pytest.raises(ValueError):
            listing_uri("0000-1", "alpha", attack)


def test_listing_uri_checks_the_owner_segment_too():
    """The owner comes from caller input (``?owner=``), so it is checked."""
    for attack in ["../..", "..", "a/../../.."]:
        with pytest.raises(ValueError):
            listing_uri(attack)


def test_listing_uri_requires_an_owner_for_a_project():
    """A project name alone does not identify a resource.

    Every owner may have an ``alpha``, so there is nothing to resolve against.
    """
    with pytest.raises(ValueError):
        listing_uri(None, "alpha")
    with pytest.raises(ValueError):
        listing_uri(None, None, "memories")


def test_listing_uri_two_owners_never_collide():
    a = listing_uri("0000-0001-2345-6789", "shared_name")
    b = listing_uri("0000-0002-9999-9999", "shared_name")

    assert a != b


def test_house_account_docs_are_addressable():
    """Central docs live in the same tree under a reserved owner."""
    assert (
        listing_uri(HOUSE_ACCOUNT_ID, "docs", "pitfalls")
        == "viking://resources/users/beril/docs/pitfalls"
    )


def test_user_target_root_refuses_the_house_account():
    """A user whose ORCiD is the reserved name must not own the central docs.

    ``orcid_id`` is an unvalidated String(64), so this guard is what makes the
    reservation real rather than conventional.
    """
    with pytest.raises(ReservedNamespaceError):
        user_target_root(HOUSE_ACCOUNT_ID, "anything")


def test_user_target_root_still_serves_real_orcids():
    assert user_target_root("0000-1", "alpha") == (
        "viking://resources/users/0000-1/alpha"
    )


# ---------------------------------------------------------------------------
# OpenVikingManager.insert_files
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

    result = await manager.insert_files(
        [_ingest_file(content=b"file body")], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "queued"
    assert result.results[0].uri == "viking://root/proj/notes.md"
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

    result = await manager.insert_files(
        [_ingest_file(path="figures/figure_1.png", content=b"png")],
        target_root="viking://root/proj",
    )

    assert len(result.results) == 1
    assert result.results[0].uri == "viking://root/proj/figures/figure_1.png"
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

    await manager.insert_files(
        [_ingest_file(path="a/b/c/deep.json", content=b"{}")],
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

    result = await manager.insert_files(
        [_ingest_file(path="/etc/passwd")], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "failed"
    patched_sdk.add_resource.assert_not_awaited()


async def test_insert_file_cleans_up_temp_file(settings, patched_sdk):
    spilled = {}

    async def capture(path, **kwargs):
        spilled["path"] = path
        return {}

    patched_sdk.add_resource = AsyncMock(side_effect=capture)
    manager = OpenVikingManager(settings, "user-key")

    await manager.insert_files([_ingest_file()], target_root="viking://root/proj")

    assert not Path(spilled["path"]).exists()


async def test_insert_file_cleans_up_temp_file_on_failure(settings, patched_sdk):
    """A failed submission must not leak the spilled file."""
    spilled = {}

    async def boom(path, **kwargs):
        spilled["path"] = path
        raise SdkOpenVikingError("rejected")

    patched_sdk.add_resource = AsyncMock(side_effect=boom)
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_files(
        [_ingest_file()], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "failed"
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

    result = await manager.insert_files(
        [_ingest_file(path="fig.png", content=blob)], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "queued"
    assert seen["content"] == blob


async def test_insert_file_reports_unsafe_path_without_calling_backend(
    settings, patched_sdk
):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_files(
        [_ingest_file(path="../escape.md")], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "failed"
    assert result.results[0].uri is None
    patched_sdk.add_resource.assert_not_awaited()


async def test_insert_file_closes_the_client(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    await manager.insert_files([_ingest_file()], target_root="viking://root/proj")

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

    result = await manager.insert_files(
        [_ingest_file()], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "failed"
    # The reason is generic — it must not name the backend.
    assert "openviking" not in (result.results[0].reason or "").lower()


async def test_insert_file_propagates_unexpected_errors(settings, patched_sdk):
    """A bug in our own code must surface, not be reported as a bad file."""
    patched_sdk.add_resource = AsyncMock(side_effect=TypeError("bug"))
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(TypeError):
        await manager.insert_files([_ingest_file()], target_root="viking://root/proj")


async def test_insert_file_captures_task_id(settings, patched_sdk):
    """The submission's task id is kept so the ingest stays pollable."""
    patched_sdk.add_resource = AsyncMock(
        return_value={"status": "success", "task_id": "task-abc"}
    )
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_files(
        [_ingest_file()], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].task_id == "task-abc"


async def test_insert_file_tolerates_missing_task_id(settings, patched_sdk):
    patched_sdk.add_resource = AsyncMock(return_value={})
    manager = OpenVikingManager(settings, "user-key")

    result = await manager.insert_files(
        [_ingest_file()], target_root="viking://root/proj"
    )

    assert len(result.results) == 1
    assert result.results[0].status == "queued"
    assert result.results[0].task_id is None


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


# ---------------------------------------------------------------------------
# Pitfall fragment collapsing
# ---------------------------------------------------------------------------

# Real URIs from a live backend: the store decomposes each document into a
# tree, turning section headings into path segments with a content-hash suffix.
_DOC = "viking://resources/users/beril/docs/pitfalls/pitfalls"
_FRAG_A = f"{_DOC}/BERDL_Common_Pitfalls/Pandas-Specific_Issues/gene_func_7more_c5df409f_1.md"
_FRAG_B = f"{_DOC}/BERDL_Common_Pitfalls/Pandas-Specific_Issues/NaN_Handling_2more_41c951d9.md"
_MEMORY = "viking://resources/users/0009-1/skip_probe/memories/pitfalls.md"


def test_is_synthetic_node_flags_backend_stubs():
    """Directory overviews and generated abstracts are structure, not content."""
    assert is_synthetic_node(f"{_DOC}/.overview.md")
    assert is_synthetic_node(f"{_MEMORY}/.abstract.md")
    assert not is_synthetic_node(_FRAG_A)


def test_source_document_collapses_central_doc_fragments():
    """Central docs decompose under their slug directory, not a file.

    Every segment ends in ``.md`` there, including the leaf, so a
    first-``.md`` rule would return the fragment and collapse nothing.
    """
    root = "viking://resources/users/"
    assert source_document(_FRAG_A, root) == (
        "viking://resources/users/beril/docs/pitfalls"
    )
    assert source_document(_FRAG_A, root) == source_document(_FRAG_B, root)


def test_source_document_separates_distinct_central_docs():
    root = "viking://resources/users/"
    pitfalls = source_document(_FRAG_A, root)
    performance = source_document(
        "viking://resources/users/beril/docs/performance/performance/G/x.md", root
    )

    assert pitfalls != performance


def test_source_document_takes_the_first_md_segment():
    root = "viking://resources/users/"
    assert source_document(f"{_MEMORY}/{'chunk_1.md'}", root) == _MEMORY


def test_source_document_returns_the_uri_when_no_document_is_found():
    """Better to report the node than to guess at a grouping."""
    root = "viking://resources/users/"
    assert source_document("viking://resources/users/0009-1", root) == (
        "viking://resources/users/0009-1"
    )


def test_collapse_fragments_groups_and_ranks():
    nodes = [
        {"uri": _FRAG_A, "score": 0.67, "text": "pandas blows up"},
        {"uri": _FRAG_B, "score": 0.62, "text": "NaN handling"},
        {"uri": f"{_MEMORY}/c.md", "score": 0.88, "text": "spark OOM"},
    ]
    out = _collapse_fragments(nodes, limit=10)

    assert len(out) == 2
    # The project memory scored highest, so it leads.
    assert out[0]["uri"] == _MEMORY
    # The document's score is its best fragment's, not an average.
    assert out[1]["score"] == 0.67
    assert len(out[1]["fragment_uris"]) == 2


def test_collapse_fragments_drops_synthetic_nodes():
    nodes = [
        {"uri": f"{_DOC}/.overview.md", "score": 0.99, "text": ""},
        {"uri": f"{_MEMORY}/.abstract.md", "score": 0.95, "text": "a summary"},
        {"uri": _FRAG_A, "score": 0.10, "text": "real content"},
    ]
    out = _collapse_fragments(nodes, limit=10)

    # The stubs outscored the real hit and are still gone.
    assert len(out) == 1
    assert out[0]["fragment_uris"] == [_FRAG_A]


def test_collapse_fragments_caps_excerpts_and_dedups():
    nodes = [
        {"uri": f"{_DOC}/f{i}.md", "score": 0.5, "text": "same text"}
        for i in range(5)
    ]
    nodes.append({"uri": f"{_DOC}/f9.md", "score": 0.5, "text": "different"})
    out = _collapse_fragments(nodes, limit=10)

    assert len(out) == 1
    # Duplicates collapse; the cap keeps the response from restating the doc.
    assert out[0]["excerpts"] == ["same text", "different"]
    assert len(out[0]["fragment_uris"]) == 6


def test_collapse_fragments_honors_the_limit():
    nodes = [
        {"uri": f"viking://resources/users/o/p{i}/memories/pitfalls.md/x.md",
         "score": i / 10, "text": "t"}
        for i in range(10)
    ]
    out = _collapse_fragments(nodes, limit=3)

    assert len(out) == 3
    assert [round(d["score"], 1) for d in out] == [0.9, 0.8, 0.7]


def test_grep_nodes_normalizes_matches():
    """Grep carries no score, so every exact match is equally exact."""
    payload = {
        "matches": [
            {"line": 3, "uri": _FRAG_A, "content": "  pandas blows up  "},
            {"line": 5, "uri": _FRAG_A, "content": "more"},
        ]
    }
    nodes = _grep_nodes(payload)

    assert [n["score"] for n in nodes] == [1.0, 1.0]
    assert nodes[0]["text"] == "pandas blows up"


def test_grep_nodes_handles_an_empty_payload():
    assert _grep_nodes({"matches": [], "count": 0}) == []
    assert _grep_nodes({}) == []
