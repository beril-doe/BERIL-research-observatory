"""The wiki chat mode: Ask rules, wiki-only tools, and the citation filter.

An Ask turn runs on the admin-held key (``BERIL_WIKI_ASK_*``) with exactly
two tools — ``find`` and ``read`` with ``source=wiki`` — served in-process
through the SDK's MCP server, so the agent can reach nothing but the wiki.
``find`` numbers its results ``[n]``; the turn remembers which numbers it
handed out, and :func:`filter_citations` drops any ``[n]`` the answer cites
that was never retrieved before the reply is stored or returned.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from claude_agent_sdk import create_sdk_mcp_server, tool

from app.context_manager.base import ContextFileNotFound
from app.context_manager.wiki import WikiManager, WikiUnavailableError

ASK_SYSTEM_PROMPT = """You answer questions about the BERIL research wiki, using only what the \
wiki's `find` and `read` tools return in this conversation.

Rules:
- Cite every claim with the result number it came from, as [n]. Cite only numbers \
you were given by `find` in this conversation; never invent one.
- Quote numbers, units, organism and gene names verbatim from the retrieved text. \
Never round, convert or paraphrase a figure.
- If the retrieved text does not answer the question, reply with exactly NO_ANSWER \
and one sentence saying what was searched.
- Do not add confidence labels, hedging scores or "likely"/"probably" qualifiers.
- Open questions and research directions in the wiki are untested proposals; say so \
when you report one.
- Keep the answer under 220 words. No preamble.
- Use `find` first; `read` a page only when a result's text is not enough."""

TOOL_FIND = "mcp__wiki__find"
TOOL_READ = "mcp__wiki__read"
ALLOWED_TOOLS = [TOOL_FIND, TOOL_READ]

_CITATION = re.compile(r"\[(\d{1,3})\]")
_RESULT_LINE = re.compile(r"^\[(\d{1,3})\] ", re.MULTILINE)


def filter_citations(text: str, allowed: set[int]) -> str:
    """Drop every ``[n]`` whose ``n`` was not retrieved this turn."""
    return _CITATION.sub(lambda m: m.group(0) if int(m.group(1)) in allowed else "", text)


def cited_numbers(tool_result_text: str) -> set[int]:
    """The ``[n]`` numbers a ``find`` result handed out."""
    return {int(n) for n in _RESULT_LINE.findall(tool_result_text or "")}


@dataclass
class WikiTurn:
    """What one Ask turn retrieved: the numbers it may cite and the hits
    behind them, so a reply can be checked and its sources shown."""

    retrieved: dict[int, dict] = field(default_factory=dict)
    next_number: int = 1

    @property
    def allowed(self) -> set[int]:
        return set(self.retrieved)

    def number(self, hits: list[dict]) -> list[tuple[int, dict]]:
        numbered = []
        for hit in hits:
            self.retrieved[self.next_number] = hit
            numbered.append((self.next_number, hit))
            self.next_number += 1
        return numbered


def format_find(numbered: list[tuple[int, dict]]) -> str:
    if not numbered:
        return "No results."
    lines = []
    for n, hit in numbered:
        heading = f" › {hit['heading']}" if hit.get("heading") else ""
        lines.append(f"[{n}] {hit['title']}{heading} ({hit['address']})\n{hit['text']}".strip())
    return "\n\n".join(lines)


def build_wiki_tools(manager: WikiManager, turn: WikiTurn, *, find_limit: int = 8):
    """The in-process MCP server exposing ``find`` and ``read`` over the wiki."""
    return create_sdk_mcp_server(name="wiki", version="1.0.0", tools=wiki_tools(manager, turn, find_limit=find_limit))


def wiki_tools(manager: WikiManager, turn: WikiTurn, *, find_limit: int = 8) -> list:
    """The two tools as ``SdkMcpTool`` definitions (``.handler`` is callable
    directly). Both record into ``turn``; both report wiki outages as tool
    errors so the agent can say NO_ANSWER rather than the turn failing."""

    @tool(
        "find",
        "Search the BERIL wiki. Returns numbered results [n] with the page, heading "
        "and matching text; cite these numbers.",
        {"query": str, "scope": str},
    )
    async def find(args):
        try:
            found = await manager.find(
                str(args.get("query") or ""), scope=args.get("scope") or None, limit=find_limit
            )
        except WikiUnavailableError as exc:
            return {"content": [{"type": "text", "text": f"wiki unavailable: {exc}"}], "is_error": True}
        return {"content": [{"type": "text", "text": format_find(turn.number(found["results"]))}]}

    @tool(
        "read",
        "Read one wiki page in full by its address (wiki/<collection>/<slug>).",
        {"address": str},
    )
    async def read(args):
        try:
            file, extra = await manager.read(str(args.get("address") or ""))
        except (ValueError, ContextFileNotFound) as exc:
            return {"content": [{"type": "text", "text": f"no such page: {exc}"}], "is_error": True}
        except WikiUnavailableError as exc:
            return {"content": [{"type": "text", "text": f"wiki unavailable: {exc}"}], "is_error": True}
        header = f"# {extra['title']}\n({extra['link']})\n\n"
        return {"content": [{"type": "text", "text": header + file.content}]}

    return [find, read]
