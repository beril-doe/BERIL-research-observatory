"""The SDK and the server must agree on request shapes.

Why this exists: ``openviking_sdk`` forwards every field its typed option
dicts declare, and the ``openviking`` server rejects any field it does not
know (``extra="forbid"``). The two are released in step but only loosely
coupled in metadata — the server declares a floor on the SDK, the SDK declares
nothing about the server — so an SDK one release ahead of the server turns a
valid-looking call into a 422 on every request. That is exactly how
``read_content=True`` on ``/api/context/find`` returned 502 unconditionally
against server 0.4.15 while every unit test (which mocks the SDK) stayed green.

These tests run against the *installed* pair, so a future skew fails here
instead of in production. They need the server package importable, which the
root project provides; in an environment without it they skip rather than
pretend.
"""

from __future__ import annotations

import inspect
import pathlib
import re

import pytest

openviking_sdk = pytest.importorskip("openviking_sdk")
search_router = pytest.importorskip("openviking.server.routers.search")
resources_router = pytest.importorskip("openviking.server.routers.resources")

from openviking_sdk.client import AsyncHTTPClient

# Option keys that are containers or SDK-side mechanics, not request fields.
# ``extra`` is a passthrough bag the SDK merges into the body; ``image`` is
# renamed to ``image_url`` on the wire by ``_search_options_payload``.
_NOT_WIRE_FIELDS = {"extra"}
_RENAMED = {"image": "image_url"}


def _declared(options_type) -> set[str]:
    keys = set(getattr(options_type, "__optional_keys__", ()))
    keys |= set(getattr(options_type, "__required_keys__", ()))
    return {_RENAMED.get(k, k) for k in keys} - _NOT_WIRE_FIELDS


def _fields(model) -> set[str]:
    return set(model.model_fields)


def test_find_options_are_all_known_to_the_server():
    """Every FindOptions key the SDK can forward is a FindRequest field."""
    unknown = _declared(openviking_sdk.FindOptions) - _fields(search_router.FindRequest)
    assert not unknown, (
        f"SDK FindOptions forwards {sorted(unknown)} but the installed server's "
        f"FindRequest does not declare them — with extra='forbid' these 422 on "
        f"every call. SDK and server pins are out of step."
    )


def test_find_body_the_sdk_builds_validates_against_the_server():
    """The strongest form: serialize through the SDK's real code path, then
    validate with the server's real model. Exercises the field renames and
    None-dropping too."""
    options = {
        "read_content": True,
        "score_threshold": 0.5,
        "filter": {"op": "must", "field": "uri", "conds": ["viking://x/"]},
        "since": "7d",
        "until": "2026-01-01",
        "time_field": "created_at",
        "node_limit": 50,
    }
    body = AsyncHTTPClient._search_options_payload(
        "query text",
        options,
        openviking_sdk.FindOptions,
        fixed={"target_uri": "viking://resources/users", "limit": 10},
    )
    # Raises pydantic.ValidationError on any unknown or malformed field.
    search_router.FindRequest(**body)


def test_grep_arguments_are_all_known_to_the_server():
    """``grep`` has no typed options dict — it takes direct keyword arguments
    and sends each one as a body field — so the contract is its signature."""
    import inspect

    sent = set(inspect.signature(AsyncHTTPClient.grep).parameters) - {"self"}
    unknown = sent - _fields(search_router.GrepRequest)
    assert not unknown, f"SDK grep() sends unknown GrepRequest fields: {sorted(unknown)}"


def test_add_resource_options_are_all_known_to_the_server():
    unknown = _declared(openviking_sdk.AddResourceOptions) - _fields(
        resources_router.AddResourceRequest
    )
    assert not unknown, (
        f"SDK AddResourceOptions forwards unknown AddResourceRequest fields: {sorted(unknown)}"
    )


def test_find_response_carries_the_fields_beril_maps():
    """BERIL's QueryResult reads these per-hit keys from the find response.

    Checked against the server's own code rather than a hand-written payload —
    a test that fabricates a response proves nothing about the server, which
    is how a mapped field the server never produced went unnoticed.

    Two sources, because the server builds a hit in two places: the base keys
    come from the hit serializer in ``openviking_cli.retrieve.types``, and
    ``content`` is attached afterwards by the find router's
    ``_inline_read_content`` when ``read_content`` is set.
    """
    import inspect

    from openviking_cli.retrieve import types as retrieve_types

    serializer = inspect.getsource(retrieve_types)
    for key in ("uri", "score", "abstract", "context_type", "match_reason"):
        assert f'"{key}"' in serializer, (
            f"BERIL maps {key!r} from a find hit, but the installed server's hit "
            f"serializer never emits it"
        )

    router = inspect.getsource(search_router)
    assert "_inline_read_content" in router and '"content"' in router, (
        "BERIL maps 'content' from a find hit, but the installed server has no "
        "read_content path that attaches it — this is the 0.4.15 gap"
    )



# --- the interactive scripts' direct client ----------------------------------
#
# ``ingest_context.py``'s interactive modes and ``knowledge_query.py`` drive
# ``openviking.SyncHTTPClient`` directly, not through BERIL. The 0.4.15 → 0.4.22
# pin moved ``add_resource``'s ``reason`` into ``options`` and dropped
# ``link``/``unlink``/``relations`` entirely; both scripts still called them,
# and the test fakes accepted the old shapes, so nothing failed until a real
# ``--docs`` run. These pin the calls the scripts make against the installed
# client.

_ov = pytest.importorskip("openviking")

# Every method observatory_context / knowledge_query call on the OV client,
# with the keyword arguments they pass.
_SCRIPT_CALLS = {
    "add_resource": {"path", "to", "wait", "options"},
    "rm": {"recursive"},
    "wait_processed": set(),
    "find": set(),
    "grep": set(),
    "glob": {"uri"},
    "ls": {"simple", "recursive"},
    "tree": {"node_limit"},
    "stat": set(),
    "read": set(),
    "overview": set(),
    "get_status": set(),
    "is_healthy": set(),
    "initialize": set(),
    "close": set(),
}


@pytest.mark.parametrize("method", sorted(_SCRIPT_CALLS))
def test_scripts_only_call_what_the_pinned_client_provides(method):
    client = _ov.SyncHTTPClient
    assert hasattr(client, method), (
        f"the scripts call SyncHTTPClient.{method}, which the installed openviking "
        f"does not provide"
    )
    params = inspect.signature(getattr(client, method)).parameters
    missing = _SCRIPT_CALLS[method] - set(params)
    assert not missing, f"SyncHTTPClient.{method} does not accept {sorted(missing)}"


def test_add_resource_reason_is_an_option_the_server_knows():
    """The reason goes in ``options``; it must be a field the client and the
    server both carry."""
    assert "reason" in _declared(openviking_sdk.AddResourceOptions)
    assert "reason" not in inspect.signature(_ov.SyncHTTPClient.add_resource).parameters


def test_scripts_do_not_call_relations_methods():
    """No relations API on the pinned client — the scripts must not use one."""
    root = pathlib.Path(__file__).resolve().parents[2]
    sources = list((root / "observatory_context").glob("*.py")) + [
        root / "knowledge" / "scripts" / "knowledge_query.py",
        root / "knowledge" / "scripts" / "ingest_context.py",
    ]
    calls = {
        (src.name, m)
        for src in sources
        for m in re.findall(r"\bclient\.(link|unlink|relations)\(", src.read_text())
    }
    assert not calls, f"relations calls the pinned client cannot serve: {sorted(calls)}"
