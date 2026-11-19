"""The chat routes in wiki mode: session creation, admin key, quota, filter."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select

from app.chat.providers.base import TextDelta, ToolCall, ToolResult, TurnComplete
from app.db.models import AskSpend, ChatMessage, ChatSession
from tests.test_routes_chat import (  # noqa: F401  (fixtures)
    USER_TOKEN,
    _login,
    _parse_sse,
    _patched_provider,
    client,
    session_row,
    user,
)

_ASK_ENV = {
    "BERIL_WIKI_ASK_API_KEY": "sk-admin-held",
    "BERIL_WIKI_ASK_PROVIDER": "anthropic",
    "BERIL_WIKI_ASK_MODEL": "claude-sonnet-4-6",
    "BERIL_WIKI_ASK_DAILY_TOKENS_PER_USER": "50000",
    "BERIL_WIKI_ASK_RESERVE_TOKENS_PER_TURN": "20000",
    "BERIL_WIKI_ASK_MAX_TURNS": "5",
}


@pytest.fixture
def ask_env():
    with patch.dict(os.environ, _ASK_ENV):
        import app.config as cfg

        cfg._settings = None
        yield
        cfg._settings = None


@pytest.fixture
def wiki():
    with patch("app.routes.chat.get_wiki_manager", return_value=MagicMock()):
        yield


def _events(text="Yield rises [1] but see [2]."):
    return [
        ToolCall(name="mcp__wiki__find", input={"query": "yield"}, tool_use_id="tu-1"),
        ToolResult(tool_use_id="tu-1", content="[1] A (wiki/concepts/a)\nAlpha."),
        TextDelta(text=text),
        TurnComplete(usage={"input_tokens": 1200, "output_tokens": 300}, cost_usd=0.01),
    ]


async def _wiki_session(client, db_session):
    resp = client.post("/api/chat", json={"mode": "wiki"})
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _hit(letter):
    return {"address": f"wiki/concepts/{letter}", "title": letter.upper(), "heading": None,
            "text": f"{letter} text.", "score": 1.0, "link": f"https://w/concepts/{letter}"}


def _record_retrieval(monkeypatch, *per_turn):
    """The provider is patched out, so the find tool never runs; stand in
    for it by numbering hits when each turn is prepared (default: one hit,
    ``a``, on every turn)."""
    from app.chat import ask as ask_mod

    original = ask_mod.prepare_ask_turn
    turns = iter(per_turn)

    async def prepared(*args, **kwargs):
        ctx, creds = await original(*args, **kwargs)
        ctx.wiki_turn.number(next(turns, [_hit("a")]))
        return ctx, creds

    monkeypatch.setattr("app.routes.chat.prepare_ask_turn", prepared)


async def test_create_wiki_session_uses_the_configured_provider(client, user, db_session, ask_env):
    _login(client)
    sid = await _wiki_session(client, db_session)
    row = (await db_session.execute(select(ChatSession).where(ChatSession.id == sid))).scalar_one()
    assert (row.mode, row.provider_id, row.model, row.title) == ("wiki", "anthropic", "claude-sonnet-4-6", "Ask the wiki")


async def test_create_wiki_session_is_503_without_a_key(client, user):
    _login(client)
    resp = client.post("/api/chat", json={"mode": "wiki"})
    assert resp.status_code == 503
    assert "not configured" in resp.json()["error"]


async def test_general_session_still_needs_provider_and_model(client, user):
    _login(client)
    assert client.post("/api/chat", json={"mode": "general"}).status_code == 400


async def test_wiki_turn_runs_on_the_admin_key_filters_citations_and_settles(
    client, user, db_session, ask_env, wiki, monkeypatch
):
    _login(client)
    sid = await _wiki_session(client, db_session)
    _record_retrieval(monkeypatch)
    seen = {}

    async def fake(*, db, session, user_message, credentials, profile=None, **kwargs):
        seen["key"] = credentials.values["api_key"]
        seen["profile"] = profile
        for e in _events():
            yield e

    with patch("app.chat.service.run_provider_turn", fake):
        resp = client.post(f"/api/chat/{sid}/turn", json={"message": "yield?"})  # no credentials sent

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["assistant_text"] == "Yield rises [1] but see ."
    assert body["sources"] == [{"n": 1, "address": "wiki/concepts/a", "title": "A", "heading": None,
                                "link": "https://w/concepts/a"}]
    assert seen["key"] == "sk-admin-held"
    assert seen["profile"].allowed_tools == ["mcp__wiki__find", "mcp__wiki__read"]
    assert seen["profile"].max_turns == 8
    assert "NO_ANSWER" in seen["profile"].system_prompt
    spend = (await db_session.execute(select(AskSpend).where(AskSpend.user_id == user.id))).scalar_one()
    assert (spend.tokens, spend.reservations, spend.reserved_tokens) == (1500, 0, 0)
    assert round(spend.usd, 6) == round((1200 * 3.0 + 300 * 15.0) / 1e6, 6)
    stored = (await db_session.execute(
        select(ChatMessage).where(ChatMessage.session_id == sid, ChatMessage.role == "assistant")
    )).scalar_one()
    assert stored.content["text"] == "Yield rises [1] but see ."


async def _reserved(db_session, user_id) -> tuple[int, int]:
    """(reservations, reserved_tokens) on the user's spend rows; (0, 0) if none."""
    rows = (await db_session.execute(select(AskSpend).where(AskSpend.user_id == user_id))).scalars().all()
    for row in rows:
        await db_session.refresh(row)
    return sum(r.reservations for r in rows), sum(r.reserved_tokens for r in rows)


@pytest.mark.parametrize("route", ["turn", "stream"])
async def test_wiki_turn_refused_by_the_concurrency_cap_reserves_nothing(
    client, user, db_session, ask_env, wiki, route
):
    from app.chat import concurrency as c
    from app.chat.concurrency import ChatConcurrencyManager, reset_concurrency_manager

    _login(client)
    sid = await _wiki_session(client, db_session)
    c._manager = ChatConcurrencyManager(per_user_cap=1)
    c._manager._user_active[user.id] = 1  # a turn already in flight elsewhere
    try:
        with patch("app.chat.service.run_provider_turn", _patched_provider(_events())):
            resp = client.post(f"/api/chat/{sid}/{route}", json={"message": "yield?"})
    finally:
        reset_concurrency_manager()

    assert resp.status_code == 429
    assert await _reserved(db_session, user.id) == (0, 0)


async def test_wiki_turn_that_fails_before_the_provider_gives_its_reservation_back(
    client, user, db_session, ask_env, wiki
):
    _login(client)
    sid = await _wiki_session(client, db_session)

    async def broken(*args, **kwargs):
        raise RuntimeError("database went away")

    with patch("app.chat.service.persist_user_message", broken), pytest.raises(RuntimeError):
        client.post(f"/api/chat/{sid}/turn", json={"message": "yield?"})

    assert await _reserved(db_session, user.id) == (0, 0)


async def test_wiki_turn_that_errors_after_billable_work_is_still_charged(
    client, user, db_session, ask_env, wiki
):
    from app.chat.providers.base import ErrorEvent

    _login(client)
    sid = await _wiki_session(client, db_session)
    events = [
        TextDelta(text="partial"),
        ErrorEvent(message="provider reported terminal error: error_max_turns",
                   usage={"input_tokens": 1200, "output_tokens": 300}, cost_usd=0.01),
    ]

    with patch("app.chat.service.run_provider_turn", _patched_provider(events)):
        resp = client.post(f"/api/chat/{sid}/turn", json={"message": "yield?"})

    assert resp.status_code == 200, resp.text
    assert "error_max_turns" in resp.json()["error"]
    spend = (await db_session.execute(select(AskSpend).where(AskSpend.user_id == user.id))).scalar_one()
    await db_session.refresh(spend)
    assert (spend.tokens, spend.reservations, spend.reserved_tokens) == (1500, 0, 0)


async def test_wiki_turn_is_refused_past_the_daily_cap(client, user, db_session, ask_env, wiki):
    _login(client)
    sid = await _wiki_session(client, db_session)
    db_session.add(AskSpend(user_id=user.id, day=__import__("app.chat.quota", fromlist=["_today"])._today(),
                            tokens=40000))
    await db_session.commit()

    with patch("app.chat.service.run_provider_turn", _patched_provider(_events())):
        resp = client.post(f"/api/chat/{sid}/turn", json={"message": "yield?"})

    assert resp.status_code == 429
    body = resp.json()
    assert body["cap"] == "daily_tokens" and "resets at" in body["error"] and body["resets_at"]
    assert (await db_session.execute(select(ChatMessage))).scalars().all() == []


async def test_wiki_stream_holds_text_until_filtered(client, user, db_session, ask_env, wiki, monkeypatch):
    _login(client)
    sid = await _wiki_session(client, db_session)
    _record_retrieval(monkeypatch)
    with patch("app.chat.service.run_provider_turn", _patched_provider(_events())):
        resp = client.post(f"/api/chat/{sid}/stream", json={"message": "yield?"})

    assert resp.status_code == 200
    frames = _parse_sse(resp.text)
    texts = [f["data"]["text"] for f in frames if f["event"] == "text_delta"]
    assert texts == ["Yield rises [1] but see ."]
    events = [f["event"] for f in frames]
    # The filtered text arrives before completion; persistence closes the stream.
    assert events.index("text_delta") < events.index("turn_complete") < events.index("turn_persisted")


async def test_wiki_turn_is_503_when_the_key_is_unset_later(client, user, db_session, ask_env, wiki):
    _login(client)
    sid = await _wiki_session(client, db_session)
    from app.config import get_settings

    get_settings().wiki_ask_api_key = None
    resp = client.post(f"/api/chat/{sid}/turn", json={"message": "x"})
    assert resp.status_code == 503


async def test_a_follow_up_turn_keeps_the_earlier_turns_citation_numbers(
    client, user, db_session, ask_env, wiki, monkeypatch
):
    """Turn 2 resumes turn 1's transcript, where [1] already means page a;
    its own results must not reuse [1], and citing turn 1's [1] stays valid."""
    _login(client)
    sid = await _wiki_session(client, db_session)
    _record_retrieval(monkeypatch, [_hit("a")], [_hit("b")])

    with patch("app.chat.service.run_provider_turn", _patched_provider(_events("A says [1]."))):
        first = client.post(f"/api/chat/{sid}/turn", json={"message": "a?"}).json()
    with patch("app.chat.service.run_provider_turn", _patched_provider(_events("B says [2]; A said [1]."))):
        second = client.post(f"/api/chat/{sid}/turn", json={"message": "and b?"}).json()

    assert [(s["n"], s["address"]) for s in first["sources"]] == [(1, "wiki/concepts/a")]
    assert second["assistant_text"] == "B says [2]; A said [1]."
    assert [(s["n"], s["address"]) for s in second["sources"]] == [
        (1, "wiki/concepts/a"), (2, "wiki/concepts/b"),
    ]


@pytest.mark.parametrize("route", ["turn", "stream"])
async def test_wiki_turn_that_ends_without_usage_is_charged_its_reservation(
    client, user, db_session, ask_env, wiki, route
):
    """The provider ran but no terminal accounting arrived (stream cut,
    connection dropped): the turn keeps its reservation as its charge."""
    _login(client)
    sid = await _wiki_session(client, db_session)

    async def cut_off(**kwargs):
        yield TextDelta(text="partial")
        if route == "turn":
            raise ConnectionError("provider connection dropped")

    with patch("app.chat.service.run_provider_turn", cut_off):
        if route == "turn":
            with pytest.raises(ConnectionError):
                client.post(f"/api/chat/{sid}/turn", json={"message": "yield?"})
        else:
            client.post(f"/api/chat/{sid}/stream", json={"message": "yield?"})

    spend = (await db_session.execute(select(AskSpend).where(AskSpend.user_id == user.id))).scalar_one()
    await db_session.refresh(spend)
    assert (spend.tokens, spend.reservations, spend.reserved_tokens) == (20000, 0, 0)
