"""Wiki Ask quota: reservations against every cap, and settlement."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.chat.quota import QuotaExceeded, _today, next_day, next_month, reserve, settle
from app.config import Settings
from app.db.models import AskSpend, BerilUser
from sqlalchemy import select

_NO_ENV = "/dev/null/nonexistent.env"


def _settings(**overrides) -> Settings:
    base = dict(
        wiki_ask_daily_tokens_per_user=1000,
        wiki_ask_monthly_tokens=5000,
        wiki_ask_daily_usd_per_user=1.0,
        wiki_ask_monthly_usd=10.0,
        wiki_ask_max_turns=3,
    )
    base.update(overrides)
    return Settings(_env_file=_NO_ENV, **base)


@pytest.fixture
async def alice(db_session):
    u = BerilUser(orcid_id="0000-0001-0000-0001", display_name="Alice")
    db_session.add(u)
    await db_session.commit()
    return u


@pytest.fixture
async def bob(db_session):
    u = BerilUser(orcid_id="0000-0001-0000-0002", display_name="Bob")
    db_session.add(u)
    await db_session.commit()
    return u


async def _row(db_session, user):
    return (
        await db_session.execute(select(AskSpend).where(AskSpend.user_id == user.id))
    ).scalar_one()


async def test_reserve_then_settle_records_actual_usage(db_session, alice):
    settings = _settings()
    reservation = await reserve(
        db_session, settings, user_id=alice.id, turns_so_far=0, estimate_tokens=400, estimate_usd=0.2
    )
    row = await _row(db_session, alice)
    assert (row.reserved_tokens, row.reserved_usd, row.reservations, row.tokens) == (400, 0.2, 1, 0)
    assert row.day == _today()

    await settle(db_session, reservation, tokens=150, usd=0.05)

    row = await _row(db_session, alice)
    assert (row.reserved_tokens, row.reservations) == (0, 0)
    assert (row.tokens, round(row.usd, 4)) == (150, 0.05)


async def test_reservations_count_against_the_daily_token_cap(db_session, alice):
    settings = _settings()
    await reserve(db_session, settings, user_id=alice.id, turns_so_far=0, estimate_tokens=600, estimate_usd=0)
    # Still in flight: 600 held, so another 600 would pass 1000.
    with pytest.raises(QuotaExceeded) as exc:
        await reserve(db_session, settings, user_id=alice.id, turns_so_far=1, estimate_tokens=600, estimate_usd=0)
    assert exc.value.cap == "daily_tokens"
    assert exc.value.resets_at == next_day(_today())
    assert "daily token quota" in exc.value.detail and "resets at" in exc.value.detail
    # Nothing was reserved by the refused call.
    assert (await _row(db_session, alice)).reservations == 1


async def test_daily_usd_cap(db_session, alice):
    settings = _settings()
    with pytest.raises(QuotaExceeded) as exc:
        await reserve(db_session, settings, user_id=alice.id, turns_so_far=0, estimate_tokens=10, estimate_usd=1.5)
    assert exc.value.cap == "daily_usd"


async def test_monthly_caps_span_users(db_session, alice, bob):
    settings = _settings(wiki_ask_daily_tokens_per_user=4000)
    r = await reserve(db_session, settings, user_id=alice.id, turns_so_far=0, estimate_tokens=3000, estimate_usd=0)
    await settle(db_session, r, tokens=3000, usd=0.0)
    with pytest.raises(QuotaExceeded) as exc:
        await reserve(db_session, settings, user_id=bob.id, turns_so_far=0, estimate_tokens=2500, estimate_usd=0)
    assert exc.value.cap == "monthly_tokens"
    assert exc.value.resets_at == next_month(_today())
    # Under the monthly cap, Bob is fine.
    await reserve(db_session, settings, user_id=bob.id, turns_so_far=0, estimate_tokens=1000, estimate_usd=0)


async def test_monthly_usd_cap(db_session, alice, bob):
    settings = _settings(wiki_ask_daily_usd_per_user=8.0)
    r = await reserve(db_session, settings, user_id=alice.id, turns_so_far=0, estimate_tokens=1, estimate_usd=7.0)
    await settle(db_session, r, tokens=1, usd=7.0)
    with pytest.raises(QuotaExceeded) as exc:
        await reserve(db_session, settings, user_id=bob.id, turns_so_far=0, estimate_tokens=1, estimate_usd=4.0)
    assert exc.value.cap == "monthly_usd"


async def test_max_turns_per_conversation(db_session, alice):
    with pytest.raises(QuotaExceeded) as exc:
        await reserve(db_session, _settings(), user_id=alice.id, turns_so_far=3, estimate_tokens=1, estimate_usd=0)
    assert exc.value.cap == "max_turns"
    assert "3-turn" in exc.value.detail


async def test_every_cap_is_a_setting(monkeypatch):
    monkeypatch.setenv("BERIL_WIKI_ASK_DAILY_USD_PER_USER", "0.5")
    monkeypatch.setenv("BERIL_WIKI_ASK_MONTHLY_USD", "7")
    monkeypatch.setenv("BERIL_WIKI_ASK_RESERVE_TOKENS_PER_TURN", "123")
    s = Settings(_env_file=_NO_ENV)
    assert (s.wiki_ask_daily_usd_per_user, s.wiki_ask_monthly_usd, s.wiki_ask_reserve_tokens_per_turn) == (0.5, 7.0, 123)


def test_reset_instants():
    assert next_day(date(2026, 11, 30)) == datetime(2026, 12, 1, tzinfo=timezone.utc)
    assert next_month(date(2026, 12, 13)) == datetime(2027, 1, 1, tzinfo=timezone.utc)
    assert next_month(date(2026, 2, 1)) == datetime(2026, 3, 1, tzinfo=timezone.utc)
