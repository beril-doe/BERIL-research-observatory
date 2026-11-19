"""``source=wiki`` on ``/find``, ``/ls`` and ``/read``, with the wiki manager
patched out."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.context_manager.base import ContextFile, ContextFileNotFound
from app.context_manager.wiki import WikiUnavailableError
from tests.test_routes_context import _login, client, credentialed_user, manager, user  # noqa: F401

LINK = "https://beril.kbase.us/wiki/concepts/carbon-yield#key-findings"
FOUND = {
    "artifact": "site-42",
    "results": [
        {"address": "wiki/concepts/carbon-yield", "title": "Carbon yield", "heading": "Key Findings",
         "text": "Yield rises.", "score": 0.9, "link": LINK},
    ],
}
PAGE = ContextFile.from_bytes(
    b"# Carbon yield\n", address="wiki/concepts/carbon-yield", owner="wiki", project="concepts",
    path="carbon-yield.md", source="wiki", content_type="text/markdown",
)
EXTRA = {"artifact": "site-42", "title": "Carbon yield", "link": LINK, "sources": ["alpha"]}


@pytest.fixture
def wiki():
    inst = MagicMock()
    inst.find = AsyncMock(return_value=FOUND)
    inst.read = AsyncMock(return_value=(PAGE, EXTRA))
    inst.ls = AsyncMock(return_value=[{"address": "wiki/concepts/carbon-yield", "title": "Carbon yield"}])
    with patch("app.routes.context.get_wiki_manager", return_value=inst):
        yield inst


async def test_find_with_source_wiki_returns_wiki_hits_with_links(client, credentialed_user, wiki, manager):
    _login(client)
    resp = client.post("/api/context/find", json={"query": "carbon yield", "source": "wiki", "path": "concepts", "limit": 5})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["artifact"] == "site-42"
    hit = body["results"][0]
    assert (hit["address"], hit["title"], hit["link"], hit["context_type"]) == (
        "wiki/concepts/carbon-yield", "Carbon yield", LINK, "wiki_page"
    )
    assert hit["match_reason"] == "Key Findings"
    wiki.find.assert_awaited_once_with("carbon yield", scope="concepts", limit=5)
    # The context store was never asked.
    manager.query.assert_not_awaited()


async def test_find_default_source_is_the_context_store(client, credentialed_user, wiki, manager):
    _login(client)
    client.post("/api/context/find", json={"query": "alpha"})
    wiki.find.assert_not_awaited()
    manager.query.assert_awaited_once()


async def test_read_with_source_wiki_returns_the_page_with_artifact_and_link(client, credentialed_user, wiki):
    _login(client)
    resp = client.get("/api/context/read", params={"address": "wiki/concepts/carbon-yield", "source": "wiki"})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert (body["source"], body["content"], body["artifact"], body["link"]) == (
        "wiki", "# Carbon yield\n", "site-42", LINK
    )
    assert (body["title"], body["sources"]) == ("Carbon yield", ["alpha"])
    assert body["sha256"]


async def test_read_wiki_as_octet_stream(client, credentialed_user, wiki):
    _login(client)
    resp = client.get("/api/context/read", params={"address": "wiki/concepts/carbon-yield", "source": "wiki"},
                      headers={"Accept": "application/octet-stream"})
    assert resp.content == b"# Carbon yield\n"
    assert resp.headers["x-content-source"] == "wiki"


async def test_read_wiki_authors_is_404_without_asking(client, credentialed_user, wiki):
    _login(client)
    assert client.get("/api/context/read", params={"address": "wiki/authors/jane", "source": "wiki"}).status_code == 404
    wiki.read.assert_not_awaited()


async def test_read_wiki_bad_address_and_missing_page(client, credentialed_user, wiki):
    _login(client)
    wiki.read.side_effect = ValueError("bad")
    assert client.get("/api/context/read", params={"address": "wiki/concepts", "source": "wiki"}).status_code == 422
    wiki.read.side_effect = ContextFileNotFound("gone")
    assert client.get("/api/context/read", params={"address": "wiki/concepts/nope", "source": "wiki"}).status_code == 404


async def test_ls_with_source_wiki_lists_a_collection(client, credentialed_user, wiki, manager):
    _login(client)
    resp = client.get("/api/context/ls", params={"source": "wiki", "path": "wiki/concepts"})
    assert resp.status_code == 200
    assert resp.json() == [{"address": "wiki/concepts/carbon-yield", "title": "Carbon yield"}]
    wiki.ls.assert_awaited_once_with("wiki/concepts")
    manager.list_files.assert_not_awaited()


async def test_source_must_be_context_or_wiki(client, credentialed_user, wiki):
    _login(client)
    assert client.get("/api/context/ls", params={"source": "nope"}).status_code == 422
    assert client.post("/api/context/find", json={"query": "x", "source": "nope"}).status_code == 422


async def test_wiki_unavailable_is_503(client, credentialed_user, wiki):
    _login(client)
    wiki.find.side_effect = WikiUnavailableError("down")
    wiki.read.side_effect = WikiUnavailableError("down")
    wiki.ls.side_effect = WikiUnavailableError("down")

    for resp in (
        client.post("/api/context/find", json={"query": "x", "source": "wiki"}),
        client.get("/api/context/read", params={"address": "wiki/concepts/x", "source": "wiki"}),
        client.get("/api/context/ls", params={"source": "wiki"}),
    ):
        assert resp.status_code == 503
        assert resp.json() == {"detail": "wiki unavailable"}


def test_wiki_routes_require_a_login(client):
    assert client.post("/api/context/find", json={"query": "x", "source": "wiki"}).status_code == 401
    assert client.get("/api/context/read", params={"address": "wiki/concepts/x", "source": "wiki"}).status_code == 401
