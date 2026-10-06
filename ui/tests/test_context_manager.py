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
    DEFAULT_GREP_NODE_LIMIT,
    DEFAULT_LS_NODE_LIMIT,
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
    context_slugify,
    corpus_root,
    get_user_ov_api_key,
    listing_uri,
    target_uri,
    user_namespace_root,
    user_target_root,
)
from app.crypto import CredentialEncryptionError, decrypt_secret, encrypt_secret
from app.db.crud import get_ov_credential
from app.db.models import BerilUser, OvUserCredential
from cryptography.fernet import Fernet
from openviking_sdk.errors import NotFoundError as SdkNotFoundError
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

# The backend's grep payload for no matches, as server 0.4.22 returns it.
EMPTY_GREP = {"matches": [], "count": 0, "match_count": 0, "files_scanned": 0}

# The default read target: the whole corpus. ``query`` requires one — the
# route resolves it, so a test that does not care about scope passes this.
CORPUS = "viking://resources/users"

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
    inst.grep = AsyncMock(return_value=dict(EMPTY_GREP))
    inst.glob = AsyncMock(return_value={"matches": [], "count": 0})
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
    out = await manager.query(ContextQuery(query="alpha"), target_uri=CORPUS)

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
        ContextQuery(query="alpha", limit=5, score_threshold=0.5),
        target_uri="viking://resources/users/0000-1/alpha",
    )

    patched_sdk.find.assert_awaited_once_with(
        "alpha",
        limit=5,
        target_uri="viking://resources/users/0000-1/alpha",
        options={"score_threshold": 0.5},
    )


async def test_query_searches_the_given_target_not_the_query(settings, patched_sdk):
    """The query's addressing fields are the route's to resolve; the manager
    searches exactly the target it is handed and never derives one itself."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(
        ContextQuery(query="alpha", project="alpha", owner="0000-9", path="x"),
        target_uri="viking://resources/users/0000-1/beta",
    )

    assert patched_sdk.find.await_args.kwargs["target_uri"] == (
        "viking://resources/users/0000-1/beta"
    )


async def test_query_forwards_several_targets_as_one_scope(settings, patched_sdk):
    """A list is passed through natively — the backend ranks across the
    URIs together, which a fan-out could not reproduce."""
    manager = OpenVikingManager(settings, "user-key")
    targets = ["viking://resources/users/a/alpha", "viking://resources/users/b/alpha"]
    await manager.query(ContextQuery(query="alpha"), target_uri=targets)

    assert patched_sdk.find.await_args.kwargs["target_uri"] == targets


async def test_query_with_no_targets_never_reaches_the_backend(settings, patched_sdk):
    """An empty target would fall back to the backend's own scope, which is
    wider than the corpus — so it is answered here, with nothing."""
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha"), target_uri=[])

    assert isinstance(out, ContextQueryResults)
    assert (out.query, out.results, out.total) == ("alpha", [], 0)
    patched_sdk.find.assert_not_awaited()
    patched_sdk.initialize.assert_not_awaited()


async def test_query_forwards_the_extended_options(settings, patched_sdk):
    """Time bounds, node limit and read_content all reach the backend."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(
        ContextQuery(
            query="alpha",
            limit=5,
            score_threshold=0.5,
            since="7d",
            until="2026-01-01",
            time_field="created_at",
            node_limit=50,
            read_content=True,
        ),
        target_uri=CORPUS,
    )

    assert patched_sdk.find.await_args.kwargs["options"] == {
        "score_threshold": 0.5,
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
    await manager.query(ContextQuery(query="alpha"), target_uri=CORPUS)

    assert patched_sdk.find.await_args.kwargs["options"] is None


async def test_query_omits_read_content_when_false(settings, patched_sdk):
    """``read_content=False`` is the default, so it is not sent at all."""
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(
        ContextQuery(query="alpha", read_content=False), target_uri=CORPUS
    )

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
    out = await manager.query(
        ContextQuery(query="alpha", read_content=True), target_uri=CORPUS
    )

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
    out = await manager.query(ContextQuery(query="alpha", limit=1), target_uri=CORPUS)

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
    out = await manager.query(ContextQuery(query="alpha"), target_uri=CORPUS)

    assert out.total == 2


async def test_query_tolerates_missing_fields_in_a_hit(settings, patched_sdk):
    """A hit missing uri/score/abstract maps to empty values, not a 500."""
    patched_sdk.find.return_value = {"resources": [{}]}
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.query(ContextQuery(query="alpha"), target_uri=CORPUS)

    r = out.results[0]
    assert (r.uri, r.context_type, r.score, r.text) == ("", "", 0.0, "")


async def test_query_closes_the_client_when_find_raises(settings, patched_sdk):
    """A failed query must not leak the connection."""
    patched_sdk.find.side_effect = UnavailableError("backend down")
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(UnavailableError):
        await manager.query(ContextQuery(query="alpha"), target_uri=CORPUS)

    patched_sdk.close.assert_awaited_once()


async def test_query_handles_empty_resources(settings, patched_sdk):
    patched_sdk.find.return_value = {"resources": []}
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.query(ContextQuery(query="nothing"), target_uri=CORPUS)

    assert out.results == []
    assert out.query == "nothing"


async def test_query_handles_missing_resources_key(settings, patched_sdk):
    """A payload with no ``resources`` key degrades to an empty result set."""
    patched_sdk.find.return_value = {}
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.query(ContextQuery(query="nothing"), target_uri=CORPUS)

    assert out.results == []


async def test_query_uses_the_credentialed_api_key(settings, sdk_client):
    """The manager's api_key is handed to the SDK, not the admin key."""
    with patch(
        "app.clients.openviking.AsyncHTTPClient", return_value=sdk_client
    ) as sdk_cls:
        await OpenVikingManager(settings, "per-user-key").query(
            ContextQuery(query="q"), target_uri=CORPUS
        )

    assert sdk_cls.call_args.kwargs["api_key"] == "per-user-key"


async def test_query_closes_the_client(settings, patched_sdk):
    """Regression: the per-call client must be closed, or connections leak.

    ``AsyncHTTPClient.close`` is a coroutine, so calling it without ``await``
    leaves it un-awaited and the connection open.
    """
    manager = OpenVikingManager(settings, "user-key")
    await manager.query(ContextQuery(query="alpha"), target_uri=CORPUS)

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


async def test_list_files_returns_empty_for_no_payload(settings, patched_sdk):
    patched_sdk.ls.return_value = None
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.list_files("viking://x") == []


async def test_list_files_returns_empty_for_an_unknown_path(settings, patched_sdk):
    """An un-ingested project is empty, not an error.

    The backend raises not-found for a path it does not know (verified against
    server 0.4.22) — it never answers with an empty payload — so that is what
    this must absorb.
    """
    patched_sdk.ls.side_effect = SdkNotFoundError("viking://x/never-ingested")
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.list_files("viking://x/never-ingested") == []
    patched_sdk.close.assert_awaited_once()


async def test_list_files_skips_an_unknown_path_in_a_fan_out(settings, patched_sdk):
    """One owner's copy vanishing between the glob and the read must not fail
    the others."""
    patched_sdk.ls.side_effect = [["a.md"], SdkNotFoundError("gone"), ["c.md"]]
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.list_files(["viking://x/1", "viking://x/2", "viking://x/3"])

    assert out == ["a.md", "c.md"]


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


async def test_list_files_fans_out_over_several_uris(settings, patched_sdk):
    """The backend lists one location at a time, so several are listed in
    turn and concatenated, in order, over one client."""
    patched_sdk.ls.side_effect = [["a.md"], ["b.md", "c.md"]]
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.list_files(["viking://x/one", "viking://x/two"], simple=True)

    assert out == ["a.md", "b.md", "c.md"]
    assert [c.args[0] for c in patched_sdk.ls.await_args_list] == [
        "viking://x/one", "viking://x/two"
    ]
    assert all(c.kwargs["simple"] is True for c in patched_sdk.ls.await_args_list)
    patched_sdk.initialize.assert_awaited_once()
    patched_sdk.close.assert_awaited_once()


async def test_list_files_shares_one_node_budget_across_a_fan_out(
    settings, patched_sdk
):
    """``node_limit`` bounds the whole request, not each URI: each call is
    asked for what remains, and once it is spent the rest are not listed."""
    patched_sdk.ls.side_effect = [["a", "b", "c"], ["d", "e"], ["never"]]
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.list_files(
        ["viking://x/1", "viking://x/2", "viking://x/3"], node_limit=5
    )

    assert out == ["a", "b", "c", "d", "e"]
    assert [c.kwargs["node_limit"] for c in patched_sdk.ls.await_args_list] == [5, 2]


async def test_list_files_trims_a_backend_that_overshoots(settings, patched_sdk):
    patched_sdk.ls.side_effect = [["a", "b", "c"], ["d", "e", "f"]]
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.list_files(["viking://x/1", "viking://x/2"], node_limit=4)

    assert out == ["a", "b", "c", "d"]


async def test_list_files_fan_out_defaults_to_the_backends_single_call_budget(
    settings, patched_sdk
):
    """Omitted, the budget is what one backend call would allow — so a fan-out
    returns no more than a single-location listing would."""
    patched_sdk.ls.side_effect = [["a"], ["b"]]
    manager = OpenVikingManager(settings, "user-key")

    await manager.list_files(["viking://x/1", "viking://x/2"])

    assert [c.kwargs["node_limit"] for c in patched_sdk.ls.await_args_list] == [
        DEFAULT_LS_NODE_LIMIT, DEFAULT_LS_NODE_LIMIT - 1
    ]


async def test_list_files_with_no_uris_never_reaches_the_backend(
    settings, patched_sdk
):
    """Listing nothing is not listing nowhere: an empty target must not fall
    back to the backend's own default scope."""
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.list_files([]) == []
    patched_sdk.ls.assert_not_awaited()
    patched_sdk.initialize.assert_not_awaited()


# ---------------------------------------------------------------------------
# OpenVikingManager.glob
# ---------------------------------------------------------------------------


async def test_glob_returns_the_matched_uris(settings, patched_sdk):
    """Directory matches arrive with a trailing slash (as the live backend
    returns them); they are normalized to the form ``listing_uri`` produces."""
    patched_sdk.glob.return_value = {
        "matches": ["viking://resources/users/a/alpha/", "viking://resources/users/b/alpha/"],
        "count": 2,
    }
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.glob("*/alpha", "viking://resources/users", node_limit=50)

    assert out == ["viking://resources/users/a/alpha", "viking://resources/users/b/alpha"]
    patched_sdk.glob.assert_awaited_once_with(
        "*/alpha", uri="viking://resources/users", node_limit=50
    )
    patched_sdk.close.assert_awaited_once()


async def test_glob_omits_an_unset_node_limit(settings, patched_sdk):
    manager = OpenVikingManager(settings, "user-key")
    await manager.glob("*/alpha", "viking://resources/users")

    assert "node_limit" not in patched_sdk.glob.await_args.kwargs


@pytest.mark.parametrize("payload", [None, {}, {"matches": [], "count": 0}])
async def test_glob_with_no_matches_is_empty(settings, patched_sdk, payload):
    patched_sdk.glob.return_value = payload
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.glob("*/alpha", "viking://resources/users") == []


async def test_glob_on_an_unknown_root_is_empty(settings, patched_sdk):
    """The backend raises not-found for a root nobody has written under yet —
    an empty corpus, which is a legitimate state rather than an error."""
    patched_sdk.glob.side_effect = SdkNotFoundError("viking://resources/users")
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.glob("*/alpha", "viking://resources/users") == []
    patched_sdk.close.assert_awaited_once()


async def test_glob_closes_the_client_when_glob_raises(settings, patched_sdk):
    patched_sdk.glob.side_effect = UnavailableError("backend down")
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(UnavailableError):
        await manager.glob("*/alpha", "viking://resources/users")

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
    assert out == EMPTY_GREP


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


async def test_grep_returns_empty_for_an_unknown_path(settings, patched_sdk):
    """The backend raises not-found for a path it does not know; that matches
    nothing, in the backend's own empty shape."""
    patched_sdk.grep.side_effect = SdkNotFoundError("viking://x/never-ingested")
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.grep("viking://x/never-ingested", "pat") == EMPTY_GREP
    patched_sdk.close.assert_awaited_once()


async def test_grep_skips_an_unknown_path_in_a_fan_out(settings, patched_sdk):
    patched_sdk.grep.side_effect = [
        {"matches": [{"uri": "viking://x/1/a.md"}],
         "count": 1, "match_count": 1, "files_scanned": 2},
        SdkNotFoundError("gone"),
        {"matches": [{"uri": "viking://x/3/c.md"}],
         "count": 1, "match_count": 1, "files_scanned": 5},
    ]
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.grep(["viking://x/1", "viking://x/2", "viking://x/3"], "pat")

    assert out == {
        "matches": [{"uri": "viking://x/1/a.md"}, {"uri": "viking://x/3/c.md"}],
        "count": 2,
        "match_count": 2,
        "files_scanned": 7,
    }


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


async def test_grep_fans_out_over_several_uris_and_merges(settings, patched_sdk):
    """Several URIs are searched in turn and merged into the backend's own
    payload shape — counts recounted, files scanned summed — with the
    exclusion applied to each."""
    patched_sdk.grep.side_effect = [
        {"matches": [{"uri": "viking://x/one/a.md"}],
         "count": 1, "match_count": 1, "files_scanned": 4},
        {"matches": [{"uri": "viking://x/two/b.md"}, {"uri": "viking://x/two/c.md"}],
         "count": 2, "match_count": 2, "files_scanned": 6},
    ]
    manager = OpenVikingManager(settings, "user-key")
    out = await manager.grep(
        ["viking://x/one", "viking://x/two"], "pat", exclude_uri="viking://x/skip"
    )

    assert out == {
        "matches": [
            {"uri": "viking://x/one/a.md"},
            {"uri": "viking://x/two/b.md"},
            {"uri": "viking://x/two/c.md"},
        ],
        "count": 3,
        "match_count": 3,
        "files_scanned": 10,
    }
    assert [c.args[0] for c in patched_sdk.grep.await_args_list] == [
        "viking://x/one", "viking://x/two"
    ]
    assert all(
        c.kwargs["exclude_uri"] == "viking://x/skip"
        for c in patched_sdk.grep.await_args_list
    )
    patched_sdk.close.assert_awaited_once()


def _hits(prefix: str, n: int, scanned: int) -> dict:
    return {
        "matches": [{"uri": f"{prefix}/{i}.md"} for i in range(n)],
        "count": n,
        "match_count": n,
        "files_scanned": scanned,
    }


async def test_grep_shares_one_match_budget_across_a_fan_out(settings, patched_sdk):
    patched_sdk.grep.side_effect = [
        _hits("viking://x/1", 3, 10),
        _hits("viking://x/2", 2, 4),
        _hits("viking://x/3", 9, 9),
    ]
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.grep(
        ["viking://x/1", "viking://x/2", "viking://x/3"], "pat", node_limit=5
    )

    assert out["count"] == out["match_count"] == len(out["matches"]) == 5
    assert out["files_scanned"] == 14
    assert [c.kwargs["node_limit"] for c in patched_sdk.grep.await_args_list] == [5, 2]


async def test_grep_fan_out_defaults_to_the_backends_single_call_budget(
    settings, patched_sdk
):
    patched_sdk.grep.side_effect = [_hits("viking://x/1", 1, 1), _hits("viking://x/2", 0, 1)]
    manager = OpenVikingManager(settings, "user-key")

    await manager.grep(["viking://x/1", "viking://x/2"], "pat")

    assert [c.kwargs["node_limit"] for c in patched_sdk.grep.await_args_list] == [
        DEFAULT_GREP_NODE_LIMIT, DEFAULT_GREP_NODE_LIMIT - 1
    ]


async def test_grep_trims_a_backend_that_overshoots(settings, patched_sdk):
    patched_sdk.grep.side_effect = [_hits("viking://x/1", 3, 3), _hits("viking://x/2", 3, 3)]
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.grep(["viking://x/1", "viking://x/2"], "pat", node_limit=4)

    assert out["count"] == len(out["matches"]) == 4


async def test_grep_with_one_uri_in_a_list_returns_the_backend_payload(
    settings, patched_sdk
):
    """A single-element list is the single-URI case: the payload comes back
    untouched rather than re-shaped."""
    patched_sdk.grep.return_value = {**EMPTY_GREP, "extra": "kept"}
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.grep(["viking://x"], "pat")

    assert out == {**EMPTY_GREP, "extra": "kept"}


async def test_grep_with_no_uris_never_reaches_the_backend(settings, patched_sdk):
    """The answer has the backend's own empty shape, so a consumer cannot tell
    whether the backend was asked — and it was not."""
    manager = OpenVikingManager(settings, "user-key")

    assert await manager.grep([], "pat") == EMPTY_GREP
    patched_sdk.grep.assert_not_awaited()
    patched_sdk.initialize.assert_not_awaited()


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


async def test_task_statuses_reports_expired_task_as_expired(settings, patched_sdk):
    """A record the backend no longer has is *gone*, not merely unreachable.

    Not proof of failure — but terminal, because asking again can never learn
    more. Reporting it as ``unknown`` left the row stuck non-terminal forever.
    """
    patched_sdk.get_task = AsyncMock(return_value=None)
    manager = OpenVikingManager(settings, "user-key")

    assert (await manager.task_statuses(["t1"]))["t1"] == ("expired", None)


async def test_task_statuses_distinguishes_gone_from_unreachable(
    settings, patched_sdk
):
    """The split, in one call: None is expired, an exception is unknown.

    They call for opposite reactions downstream — stop polling vs. keep the
    last recording — so they must never collapse onto one value.
    """
    async def per_task(task_id):
        if task_id == "gone":
            return None
        if task_id == "down":
            raise httpx.ConnectError("down")
        return {"status": "completed"}

    patched_sdk.get_task = AsyncMock(side_effect=per_task)
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.task_statuses(["gone", "down", "fine"])

    assert out["gone"] == ("expired", None)
    assert out["down"] == ("unknown", None)
    assert out["fine"][0] == "completed"


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

    assert (q.project, q.owner, q.all_owners, q.path) == (None, None, False, None)
    assert q.limit == 10
    assert q.score_threshold is None


# ---------------------------------------------------------------------------
# Credential lifecycle: regenerate, unreadable ciphertext, self-heal, backfill
# ---------------------------------------------------------------------------


def _refused():
    from openviking_sdk.errors import UnauthenticatedError as SdkUnauthenticated

    return SdkUnauthenticated("key revoked")


async def _seed_credential(db_session, user, plaintext, key=None):
    db_session.add(
        OvUserCredential(
            user_id=user.id,
            account_id="beril",
            ov_user_id=user.orcid_id,
            encrypted_key=encrypt_secret(plaintext, key or _CREDENTIAL_KEY),
        )
    )
    await db_session.commit()


async def test_regenerate_replaces_the_stored_key(settings, db_session, ov_user):
    """The repair path never returns what is stored — that is the point."""
    from app.context_manager.openviking import regenerate_user_ov_api_key

    await _seed_credential(db_session, ov_user, "dead-key")
    regenerate = AsyncMock(return_value={"user_key": "fresh-key"})
    with patch("app.context_manager.openviking.regenerate_ov_user_key", regenerate), patch(
        "app.context_manager.openviking.register_ov_user"
    ) as register:
        key = await regenerate_user_ov_api_key(db_session, ov_user)

    assert key == "fresh-key"
    regenerate.assert_awaited_once_with(ov_user.orcid_id)
    register.assert_not_called()
    cred = await get_ov_credential(db_session, ov_user.id)
    assert decrypt_secret(cred.encrypted_key, _CREDENTIAL_KEY) == "fresh-key"


async def test_regenerate_requires_a_user(settings, db_session):
    from app.context_manager.openviking import regenerate_user_ov_api_key

    with pytest.raises(UnauthenticatedError):
        await regenerate_user_ov_api_key(db_session, None)


async def test_regenerate_raises_when_the_store_refuses(settings, db_session, ov_user):
    from app.context_manager.openviking import regenerate_user_ov_api_key

    regenerate = AsyncMock(side_effect=OpenVikingError("nope", status_code=502))
    with patch("app.context_manager.openviking.regenerate_ov_user_key", regenerate):
        with pytest.raises(OvProvisioningError):
            await regenerate_user_ov_api_key(db_session, ov_user)


async def test_get_key_reprovisions_when_stored_credential_is_unreadable(
    settings, db_session, ov_user
):
    """A row encrypted under a rotated Fernet key is functionally no row.

    Before, this was an unhandled CredentialEncryptionError → 500 on every
    call. Now it re-provisions over the dead row.
    """
    other_key = Fernet.generate_key().decode()
    await _seed_credential(db_session, ov_user, "unreadable", key=other_key)
    register = AsyncMock(return_value={"user_key": "fresh"})
    with patch("app.context_manager.openviking.register_ov_user", register):
        key = await get_user_ov_api_key(db_session, ov_user)

    assert key == "fresh"
    register.assert_awaited_once_with(ov_user.orcid_id)
    cred = await get_ov_credential(db_session, ov_user.id)
    assert decrypt_secret(cred.encrypted_key, _CREDENTIAL_KEY) == "fresh"


@pytest.mark.parametrize("seeded", [True, False])
async def test_get_key_refuses_a_bad_encryption_key_before_touching_the_store(
    settings, db_session, ov_user, seeded
):
    """Regression (Codex, #450): a malformed key made every stored row read as
    corrupt, so each call re-provisioned — rotating the user's upstream key —
    and then failed to store the replacement. A bad *key* is now refused before
    any register or regenerate call, with or without a stored row."""
    from app.crypto import InvalidEncryptionKeyError

    if seeded:
        await _seed_credential(db_session, ov_user, "live-key")
    register = AsyncMock(return_value={"user_key": "fresh"})
    regenerate = AsyncMock(return_value={"user_key": "fresh"})
    with patch.object(settings, "ov_credential_key", "not-a-fernet-key"), patch(
        "app.context_manager.openviking.register_ov_user", register
    ), patch("app.context_manager.openviking.regenerate_ov_user_key", regenerate):
        with pytest.raises(InvalidEncryptionKeyError):
            await get_user_ov_api_key(db_session, ov_user)

    register.assert_not_awaited()
    regenerate.assert_not_awaited()


async def test_regenerate_refuses_a_bad_encryption_key_before_rotating(
    settings, db_session, ov_user
):
    """Rotating first would invalidate the old key and leave nothing stored."""
    from app.context_manager.openviking import regenerate_user_ov_api_key
    from app.crypto import InvalidEncryptionKeyError

    regenerate = AsyncMock(return_value={"user_key": "fresh"})
    with patch.object(settings, "ov_credential_key", "not-a-fernet-key"), patch(
        "app.context_manager.openviking.regenerate_ov_user_key", regenerate
    ):
        with pytest.raises(InvalidEncryptionKeyError):
            await regenerate_user_ov_api_key(db_session, ov_user)

    regenerate.assert_not_awaited()


# --- SelfHealingContextManager ----------------------------------------------


def _healing(inner_query, rotate=None):
    from app.context_manager.openviking import SelfHealingContextManager

    inner = MagicMock()
    inner.api_key = "dead"
    inner.url = "http://store"
    inner.query = inner_query
    rotate = rotate or AsyncMock(return_value="fresh")
    return SelfHealingContextManager(inner, rotate=rotate), inner, rotate


async def test_self_healing_rotates_and_retries_once():
    manager, inner, rotate = _healing(AsyncMock(side_effect=[_refused(), "result"]))

    assert await manager.query("q") == "result"

    rotate.assert_awaited_once()
    assert inner.api_key == "fresh"
    assert inner.query.await_count == 2


async def test_self_healing_does_not_rotate_on_other_errors():
    """A 404 or an outage must never rotate a key — pointless and destructive."""
    from openviking_sdk.errors import NotFoundError

    manager, inner, rotate = _healing(AsyncMock(side_effect=NotFoundError("gone")))

    with pytest.raises(NotFoundError):
        await manager.query("q")

    rotate.assert_not_awaited()
    assert inner.api_key == "dead"


async def test_self_healing_retries_exactly_once():
    """Two refusals in a row surface as an outage — no rotate loop, and not a
    raw SDK error that a route without a catch would turn into a 500."""
    from app.context_manager.openviking import ContextUnavailableError

    manager, inner, rotate = _healing(AsyncMock(side_effect=[_refused(), _refused()]))

    with pytest.raises(ContextUnavailableError):
        await manager.query("q")

    rotate.assert_awaited_once()
    assert inner.query.await_count == 2


@pytest.mark.parametrize(
    "failure",
    [OvProvisioningError("store down"), CredentialEncryptionError("cannot store")],
)
async def test_self_healing_reports_a_failed_rotation_as_unavailable(failure):
    """Regression (Codex, #450): a rotation the store refused, or one whose new
    key could not be stored, escaped as OvProvisioningError /
    CredentialEncryptionError and became a 500 on any route without a catch."""
    from app.context_manager.openviking import ContextUnavailableError

    manager, inner, _ = _healing(
        AsyncMock(side_effect=_refused()), rotate=AsyncMock(side_effect=failure)
    )

    with pytest.raises(ContextUnavailableError) as raised:
        await manager.query("q")

    assert raised.value.__cause__ is failure
    # No retry with a key that was never obtained.
    assert inner.query.await_count == 1


async def test_task_statuses_raises_a_refused_key_so_it_can_be_repaired(
    settings, patched_sdk
):
    """Regression (Codex, #450): every exception, the refusal included, was
    folded into ``unknown``, so the healer never ran for status polling."""
    from openviking_sdk.errors import UnauthenticatedError as SdkUnauthenticated

    patched_sdk.get_task = AsyncMock(side_effect=[{"status": "completed"}, _refused()])
    manager = OpenVikingManager(settings, "dead-key")

    with pytest.raises(SdkUnauthenticated):
        await manager.task_statuses(["t1", "t2"])


async def test_task_statuses_still_folds_other_failures_into_unknown(
    settings, patched_sdk
):
    patched_sdk.get_task = AsyncMock(side_effect=[UnavailableError("down"), None])
    manager = OpenVikingManager(settings, "key")

    out = await manager.task_statuses(["t1", "t2"])

    assert out == {"t1": ("unknown", None), "t2": ("expired", None)}


async def test_task_statuses_through_the_healer_rotates_and_retries(
    settings, patched_sdk
):
    from app.context_manager.openviking import SelfHealingContextManager

    patched_sdk.get_task = AsyncMock(side_effect=[_refused(), {"status": "running"}])
    rotate = AsyncMock(return_value="fresh-key")
    manager = SelfHealingContextManager(
        OpenVikingManager(settings, "dead-key"), rotate=rotate
    )

    out = await manager.task_statuses(["t1"])

    rotate.assert_awaited_once()
    assert out == {"t1": ("processing", None)}


async def test_self_healing_passes_plain_attributes_through():
    manager, _, _ = _healing(AsyncMock())

    assert manager.url == "http://store"
    assert manager.api_key == "dead"


# --- insert_files: a refused key is not a per-file failure -------------------


async def test_insert_files_lets_a_refused_key_escape(settings, patched_sdk):
    """Every file would fail identically, so it is the batch's problem to
    retry with a fresh key — not N 'rejected' rows."""
    from openviking_sdk.errors import UnauthenticatedError as SdkUnauthenticated

    patched_sdk.add_resource = AsyncMock(side_effect=_refused())
    manager = OpenVikingManager(settings, "user-key")

    with pytest.raises(SdkUnauthenticated):
        await manager.insert_files(
            [ContextIngestFile(relative_path="a.md", content=b"x")],
            target_root="viking://resources/users/o/p",
        )


async def test_insert_files_still_records_other_errors_per_file(settings, patched_sdk):
    from openviking_sdk.errors import NotFoundError

    patched_sdk.add_resource = AsyncMock(side_effect=NotFoundError("bad target"))
    manager = OpenVikingManager(settings, "user-key")

    out = await manager.insert_files(
        [ContextIngestFile(relative_path="a.md", content=b"x")],
        target_root="viking://resources/users/o/p",
    )

    assert out.failed == 1
    assert out.results[0].status == "failed"


# --- backfill ----------------------------------------------------------------


async def _users(db_session, *orcids):
    users = [BerilUser(orcid_id=o, display_name=o) for o in orcids]
    db_session.add_all(users)
    await db_session.commit()
    for u in users:
        await db_session.refresh(u)
    return users


async def test_backfill_provisions_only_users_without_a_credential(settings, db_session):
    from app.context_manager.openviking import backfill_ov_credentials

    a, b, c = await _users(db_session, "0000-0001-0000-000A", "0000-0001-0000-000B", "0000-0001-0000-000C")
    await _seed_credential(db_session, b, "already")
    register = AsyncMock(return_value={"user_key": "k"})
    with patch("app.context_manager.openviking.register_ov_user", register):
        attempted, failed = await backfill_ov_credentials(db_session)

    assert attempted == [a.orcid_id, c.orcid_id]
    assert failed == []
    assert register.await_count == 2
    for u in (a, b, c):
        assert await get_ov_credential(db_session, u.id) is not None
    # The user who already had one was left alone.
    b_cred = await get_ov_credential(db_session, b.id)
    assert decrypt_secret(b_cred.encrypted_key, _CREDENTIAL_KEY) == "already"


async def test_backfill_dry_run_changes_nothing(settings, db_session):
    from app.context_manager.openviking import backfill_ov_credentials

    a, = await _users(db_session, "0000-0001-0000-000A")
    register = AsyncMock()
    with patch("app.context_manager.openviking.register_ov_user", register):
        attempted, failed = await backfill_ov_credentials(db_session, dry_run=True)

    assert attempted == [a.orcid_id]
    assert failed == []
    register.assert_not_awaited()
    assert await get_ov_credential(db_session, a.id) is None


async def test_backfill_records_failures_and_continues(settings, db_session):
    from app.context_manager.openviking import backfill_ov_credentials

    a, c = await _users(db_session, "0000-0001-0000-000A", "0000-0001-0000-000C")

    async def per_user(orcid):
        if orcid == a.orcid_id:
            raise OpenVikingError("down", status_code=502, code="UNAVAILABLE")
        return {"user_key": "k"}

    with patch("app.context_manager.openviking.register_ov_user", AsyncMock(side_effect=per_user)):
        attempted, failed = await backfill_ov_credentials(db_session)

    assert attempted == [a.orcid_id, c.orcid_id]
    assert [o for o, _ in failed] == [a.orcid_id]
    assert await get_ov_credential(db_session, a.id) is None
    assert await get_ov_credential(db_session, c.id) is not None


async def test_backfill_with_nothing_to_do(settings, db_session):
    from app.context_manager.openviking import backfill_ov_credentials

    assert await backfill_ov_credentials(db_session) == ([], [])


# --- startup: an unset Fernet key is refused once, not 500 per request --------


def test_require_ov_credential_key_refuses_an_unset_key():
    from app.config import Settings

    with pytest.raises(ValueError, match="BERIL_OV_CREDENTIAL_KEY"):
        Settings(ov_credential_key=None, _env_file=None).require_ov_credential_key()


def test_require_ov_credential_key_returns_it():
    from app.config import Settings

    key = Fernet.generate_key().decode()
    assert Settings(ov_credential_key=key, _env_file=None).require_ov_credential_key() == key


@pytest.mark.parametrize("bad", ["k", "not-a-fernet-key", "A" * 44])
def test_require_ov_credential_key_refuses_a_malformed_key(bad):
    """Regression (Codex, #450): a set-but-invalid key passed startup, then
    read every stored credential as corrupt and rotated upstream keys it could
    never store. It fails at startup now, like an unset one."""
    from app.config import Settings

    with pytest.raises(ValueError, match="not a valid Fernet key"):
        Settings(ov_credential_key=bad, _env_file=None).require_ov_credential_key()
