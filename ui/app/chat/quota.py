"""Wiki Ask quota: reserve before a turn, settle after it.

Every cap is a ``BERIL_WIKI_ASK_*`` setting: tokens per user per UTC day,
tokens across all users per calendar month, USD for both, turns per
conversation, and tool calls per turn (enforced by the provider's
``max_turns``). A turn first **reserves** the configured estimate (tokens,
and their USD at the model's rates) against the caps, so two turns in flight
cannot both fit under a cap only one of them would; when it finishes the
reservation is replaced by what the turn actually used. Spend is recorded
per user per day in ``ask_spend``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import AskSpend

logger = logging.getLogger(__name__)


class QuotaExceeded(Exception):
    """A cap would be passed. ``cap`` names which; ``resets_at`` is when it
    next clears, so the refusal can say so."""

    def __init__(self, cap: str, resets_at: datetime, detail: str) -> None:
        super().__init__(detail)
        self.cap = cap
        self.resets_at = resets_at
        self.detail = detail


@dataclass
class Reservation:
    user_id: str
    day: date
    tokens: int
    usd: float


def _today() -> date:
    return datetime.now(timezone.utc).date()


def next_day(day: date) -> datetime:
    return datetime.combine(day + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)


def next_month(day: date) -> datetime:
    first = date(day.year + (day.month == 12), day.month % 12 + 1, 1)
    return datetime.combine(first, datetime.min.time(), tzinfo=timezone.utc)


async def _row(db: AsyncSession, user_id: str, day: date) -> AskSpend:
    row = (
        await db.execute(select(AskSpend).where(AskSpend.user_id == user_id, AskSpend.day == day))
    ).scalar_one_or_none()
    if row is None:
        row = AskSpend(user_id=user_id, day=day)
        db.add(row)
        await db.flush()
    return row


async def _month_totals(db: AsyncSession, day: date) -> tuple[int, float]:
    """Tokens and USD, settled plus reserved, across every user this month."""
    first = day.replace(day=1)
    row = (
        await db.execute(
            select(
                func.coalesce(func.sum(AskSpend.tokens + AskSpend.reserved_tokens), 0),
                func.coalesce(func.sum(AskSpend.usd + AskSpend.reserved_usd), 0.0),
            ).where(AskSpend.day >= first, AskSpend.day < next_month(day).date())
        )
    ).one()
    return int(row[0]), float(row[1])


def _refusal(cap: str, resets_at: datetime, what: str) -> QuotaExceeded:
    when = resets_at.strftime("%Y-%m-%d %H:%M UTC")
    return QuotaExceeded(cap, resets_at, f"Wiki Ask is over its {what}; it resets at {when}.")


async def reserve(
    db: AsyncSession,
    settings: Settings,
    *,
    user_id: str,
    turns_so_far: int,
    estimate_tokens: int,
    estimate_usd: float,
) -> Reservation:
    """Hold ``estimate_tokens`` / ``estimate_usd`` for one turn, or raise
    :class:`QuotaExceeded` naming the first cap it would pass."""
    day = _today()
    if turns_so_far >= settings.wiki_ask_max_turns:
        raise QuotaExceeded(
            "max_turns", next_day(day),
            f"This conversation has reached its {settings.wiki_ask_max_turns}-turn limit; "
            "start a new one.",
        )
    row = await _row(db, user_id, day)
    if row.tokens + row.reserved_tokens + estimate_tokens > settings.wiki_ask_daily_tokens_per_user:
        raise _refusal("daily_tokens", next_day(day), "daily token quota for you")
    if row.usd + row.reserved_usd + estimate_usd > settings.wiki_ask_daily_usd_per_user:
        raise _refusal("daily_usd", next_day(day), "daily spending limit for you")
    month_tokens, month_usd = await _month_totals(db, day)
    if month_tokens + estimate_tokens > settings.wiki_ask_monthly_tokens:
        raise _refusal("monthly_tokens", next_month(day), "monthly token budget")
    if month_usd + estimate_usd > settings.wiki_ask_monthly_usd:
        raise _refusal("monthly_usd", next_month(day), "monthly spending limit")
    row.reserved_tokens += estimate_tokens
    row.reserved_usd += estimate_usd
    row.reservations += 1
    await db.commit()
    return Reservation(user_id=user_id, day=day, tokens=estimate_tokens, usd=estimate_usd)


async def settle(db: AsyncSession, reservation: Reservation, *, tokens: int, usd: float) -> None:
    """Replace a reservation with what the turn used. A turn that failed
    before using anything settles to zero."""
    row = await _row(db, reservation.user_id, reservation.day)
    row.reserved_tokens = max(0, row.reserved_tokens - reservation.tokens)
    row.reserved_usd = max(0.0, row.reserved_usd - reservation.usd)
    row.reservations = max(0, row.reservations - 1)
    row.tokens += max(0, tokens)
    row.usd += max(0.0, usd)
    await db.commit()
    logger.info(
        "Wiki Ask turn settled for %s: %d tokens, $%.4f (day total %d tokens, $%.4f)",
        reservation.user_id, tokens, usd, row.tokens, row.usd,
    )
