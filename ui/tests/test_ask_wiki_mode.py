"""Wiki mode helpers: citation filter, numbering, tools, spend arithmetic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.chat.ask import estimate_usd, spend_of
from app.chat.config import ModelInfo
from app.chat.service import TurnResult
from app.chat.wiki_mode import (
    ALLOWED_TOOLS,
    ASK_SYSTEM_PROMPT,
    WikiTurn,
    build_wiki_tools,
    cited_numbers,
    filter_citations,
    format_find,
    wiki_tools,
)
from app.context_manager.base import ContextFile
from app.context_manager.wiki import WikiUnavailableError

HITS = [
    {"address": "wiki/concepts/a", "title": "A", "heading": "Key", "text": "Alpha text.", "score": 0.9,
     "link": "https://w/concepts/a#key"},
    {"address": "wiki/topics/b", "title": "B", "heading": None, "text": "Beta text.", "score": 0.5,
     "link": "https://w/topics/b"},
]


@pytest.mark.parametrize(
    "text, allowed, expected",
    [
        ("Yield rises [1] and falls [2].", {1}, "Yield rises [1] and falls ."),
        ("No cites.", set(), "No cites."),
        ("[3][1]", {1, 3}, "[3][1]"),
        ("See [12].", {1}, "See ."),
    ],
)
def test_filter_citations(text, allowed, expected):
    assert filter_citations(text, allowed) == expected


def test_numbering_is_continuous_across_finds():
    turn = WikiTurn()
    first = turn.number(HITS[:1])
    second = turn.number(HITS[1:])
    assert [n for n, _ in first + second] == [1, 2]
    assert turn.allowed == {1, 2}
    rendered = format_find(first + second)
    assert rendered.startswith("[1] A › Key (wiki/concepts/a)\nAlpha text.")
    assert "[2] B (wiki/topics/b)" in rendered
    assert cited_numbers(rendered) == {1, 2}
    assert format_find([]) == "No results."


def test_ask_rules_are_in_the_system_prompt():
    for rule in ("[n]", "verbatim", "NO_ANSWER", "confidence", "untested", "220 words"):
        assert rule in ASK_SYSTEM_PROMPT
    assert ALLOWED_TOOLS == ["mcp__wiki__find", "mcp__wiki__read"]


def _handlers(wiki, turn):
    return {t.name: t.handler for t in wiki_tools(wiki, turn)}


async def test_find_tool_numbers_results_and_records_them():
    wiki = MagicMock()
    wiki.find = AsyncMock(return_value={"artifact": "a", "results": HITS})
    turn = WikiTurn()
    server = build_wiki_tools(wiki, turn)
    assert (server["type"], server["name"]) == ("sdk", "wiki")

    out = await _handlers(wiki, turn)["find"]({"query": "carbon", "scope": "concepts"})

    text = out["content"][0]["text"]
    assert "[1] A" in text and "[2] B" in text
    assert turn.allowed == {1, 2}
    wiki.find.assert_awaited_once_with("carbon", scope="concepts", limit=8)


async def test_tools_report_outages_as_tool_errors():
    wiki = MagicMock()
    wiki.find = AsyncMock(side_effect=WikiUnavailableError("down"))
    page = ContextFile.from_bytes(b"# A\nBody", address="wiki/concepts/a", owner="wiki", project="concepts",
                                  path="a.md", source="wiki")
    wiki.read = AsyncMock(return_value=(page, {"title": "A", "link": "https://w/concepts/a", "artifact": "x", "sources": []}))
    handlers = _handlers(wiki, WikiTurn())

    assert (await handlers["find"]({"query": "x"}))["is_error"] is True
    out = await handlers["read"]({"address": "wiki/concepts/a"})
    assert out["content"][0]["text"] == "# A\n(https://w/concepts/a)\n\n# A\nBody"

    wiki.read = AsyncMock(side_effect=ValueError("bad"))
    assert (await _handlers(wiki, WikiTurn())["read"]({"address": "nope"}))["is_error"] is True


def test_spend_arithmetic():
    model = ModelInfo(id="m", display_name="M", usd_per_million_input=3.0, usd_per_million_output=15.0)
    result = TurnResult(usage={"input_tokens": 1000, "cache_read_input_tokens": 1000, "output_tokens": 200}, cost_usd=99.0)
    tokens, usd = spend_of(result, model)
    assert tokens == 2200
    assert round(usd, 6) == round((2000 * 3.0 + 200 * 15.0) / 1e6, 6)
    # Without rates, the provider's own figure counts; without either, zero.
    assert spend_of(result, ModelInfo(id="m", display_name="M")) == (2200, 99.0)
    assert spend_of(TurnResult(), None) == (0, 0.0)
    assert estimate_usd(model, 10_000) > 0 and estimate_usd(None, 10_000) == 0.0
