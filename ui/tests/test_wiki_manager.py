"""``WikiManager`` against a mocked wiki internal API."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

import httpx
import pytest

from app.context_manager.base import ContextFileNotFound
from app.context_manager.wiki import (
    WikiManager,
    WikiUnavailableError,
    is_excluded,
    parse_wiki_address,
    quartz_anchor,
)

_ENV = {
    "BERIL_WIKI_INTERNAL_URL": "http://wiki.test:8080",
    "BERIL_WIKI_INTERNAL_TOKEN": "wiki-secret",
    "BERIL_WIKI_PUBLIC_URL": "https://beril.kbase.us/wiki",
    "BERIL_SESSION_SECRET_KEY": "s",
}

SEARCH = {
    "artifact": "site-42",
    "results": [
        {"address": "wiki/concepts/carbon-yield", "title": "Carbon yield", "heading": "Key Findings",
         "text": "Yield rises...", "score": 0.9},
        {"address": "wiki/authors/jane-doe", "title": "Jane Doe", "heading": None, "text": "x", "score": 0.8},
        {"address": "wiki/topics/fitness", "title": "Fitness", "heading": None, "text": "y", "score": 0.5},
    ],
}
PAGE = {"artifact": "site-42", "address": "wiki/concepts/carbon-yield", "title": "Carbon yield",
        "content": "# Carbon yield\n\nBody.\n", "sources": ["alpha"]}


def _wiki(handler):
    """A manager whose HTTP goes to ``handler(request) -> Response``."""
    with patch.dict(os.environ, _ENV):
        import app.config as cfg

        cfg._settings = None
        settings = cfg.get_settings()
        cfg._settings = None
    return WikiManager(settings, client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def _ok(payload):
    def handler(request):
        handler.requests.append(request)
        return httpx.Response(200, json=payload)
    handler.requests = []
    return handler


@pytest.mark.parametrize(
    "heading, anchor",
    [("Key Findings", "key-findings"), ("What's new? (2026)", "whats-new-2026"), ("  A  B ", "a-b"), ("", "")],
)
def test_quartz_anchor(heading, anchor):
    assert quartz_anchor(heading) == anchor


def test_parse_wiki_address():
    assert parse_wiki_address("wiki/concepts/carbon-yield#Key Findings") == ("concepts", "carbon-yield", "Key Findings")
    assert parse_wiki_address("wiki/sources/alpha") == ("sources", "alpha", None)
    for bad in ("concepts/x", "wiki/concepts", "wiki/authors/jane", "wiki/nope/x", "wiki/concepts/../x"):
        with pytest.raises(ValueError):
            parse_wiki_address(bad)
    assert is_excluded("wiki/authors/jane") and not is_excluded("wiki/topics/x")


async def test_find_filters_authors_and_adds_links():
    handler = _ok(SEARCH)
    found = await _wiki(handler).find("carbon yield", scope="wiki/concepts", limit=10)

    assert found["artifact"] == "site-42"
    assert [r["address"] for r in found["results"]] == ["wiki/concepts/carbon-yield", "wiki/topics/fitness"]
    assert found["results"][0]["link"] == "https://beril.kbase.us/wiki/concepts/carbon-yield#key-findings"
    assert found["results"][1]["link"] == "https://beril.kbase.us/wiki/topics/fitness"
    request = handler.requests[0]
    assert request.url.path == "/wiki/_api/search"
    assert dict(request.url.params) == {"q": "carbon yield", "k": "10", "scope": "concepts"}
    assert request.headers["authorization"] == "Bearer wiki-secret"


async def test_read_returns_a_wiki_file_with_artifact_and_link():
    file, extra = await _wiki(_ok(PAGE)).read("wiki/concepts/carbon-yield#Body")

    assert (file.source, file.content, file.address) == ("wiki", PAGE["content"], "wiki/concepts/carbon-yield#Body")
    assert file.sha256 and file.encoding == "utf-8"
    assert extra == {"artifact": "site-42", "title": "Carbon yield",
                     "link": "https://beril.kbase.us/wiki/concepts/carbon-yield#body", "sources": ["alpha"]}


async def test_read_refuses_authors_and_unknown_pages():
    with pytest.raises(ValueError):
        await _wiki(_ok(PAGE)).read("wiki/authors/jane")
    with pytest.raises(ContextFileNotFound):
        await _wiki(lambda r: httpx.Response(404, json={"detail": "no"})).read("wiki/concepts/nope")


async def test_ls_drops_excluded_collections():
    handler = _ok({"artifact": "site-42", "entries": [
        {"address": "wiki/concepts", "name": "concepts"}, {"address": "wiki/authors", "name": "authors"}]})
    assert await _wiki(handler).ls(None) == [{"address": "wiki/concepts", "name": "concepts"}]
    assert await _wiki(handler).ls("wiki/authors") == []
    await _wiki(handler).ls("wiki/concepts")
    assert dict(handler.requests[-1].url.params) == {"path": "concepts"}


async def test_errors_become_wiki_unavailable():
    def down(request):
        raise httpx.ConnectError("refused")

    with pytest.raises(WikiUnavailableError):
        await _wiki(down).find("x")
    with pytest.raises(WikiUnavailableError):
        await _wiki(lambda r: httpx.Response(500, text="boom")).find("x")
    with pytest.raises(WikiUnavailableError):
        await _wiki(lambda r: httpx.Response(200, text="not json")).find("x")


async def test_unconfigured_token_is_unavailable():
    with patch.dict(os.environ, {**_ENV, "BERIL_WIKI_INTERNAL_TOKEN": ""}):
        import app.config as cfg

        cfg._settings = None
        settings = cfg.get_settings()
        cfg._settings = None
    manager = WikiManager(settings)
    assert not manager.configured
    with pytest.raises(WikiUnavailableError):
        await manager.find("x")
    assert json.dumps(manager.link("wiki/data/x", "A B")) == '"https://beril.kbase.us/wiki/data/x#a-b"'
