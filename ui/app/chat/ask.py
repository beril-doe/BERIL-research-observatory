"""Preparing and settling one wiki Ask turn.

A turn is prepared before the provider runs — key from settings, quota
reserved, wiki tools built — and settled after it: citations filtered,
reservation replaced by actual usage. ``service`` only carries the context
through; the rules live here.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.config import ModelInfo, find_model
from app.chat.providers.base import AgentProfile, Credentials
from app.chat.quota import QuotaExceeded, Reservation, reserve, settle  # noqa: F401  (re-export)
from app.chat.wiki_mode import ALLOWED_TOOLS, ASK_SYSTEM_PROMPT, WikiTurn, build_wiki_tools, filter_citations
from app.config import Settings
from app.context_manager.wiki import WikiManager

if TYPE_CHECKING:
    from app.chat.service import TurnResult

logger = logging.getLogger(__name__)

WIKI_MODE = "wiki"
GENERAL_MODE = "general"


class AskNotConfigured(RuntimeError):
    """Wiki Ask has no admin-held key (BERIL_WIKI_ASK_API_KEY)."""


@dataclass
class AskContext:
    profile: AgentProfile
    wiki_turn: WikiTurn
    reservation: Reservation
    model: ModelInfo | None
    settled: bool = False

    async def settle(self, db: AsyncSession, result: "TurnResult") -> None:
        """Replace the reservation with what the turn used. Once only.

        Called only once the provider has been reached. A turn that ends
        there without reporting usage (client closed the stream, connection
        dropped, provider crashed) may still have done billable work, so it
        keeps the whole reservation as its charge rather than settling to
        zero."""
        if self.settled:
            return
        self.settled = True
        if result.usage is None and result.cost_usd is None:
            logger.warning(
                "Wiki Ask turn for %s ended without usage; charging its reservation",
                self.reservation.user_id,
            )
            tokens, usd = self.reservation.tokens, self.reservation.usd
        else:
            tokens, usd = spend_of(result, self.model)
        await settle(db, self.reservation, tokens=tokens, usd=usd)

    async def release(self, db: AsyncSession) -> None:
        """Give the reservation back if the turn never settled — it ended
        before reaching the provider. The routes call this on every exit."""
        if self.settled:
            return
        self.settled = True
        await settle(db, self.reservation, tokens=0, usd=0.0)


def ask_credentials(settings: Settings) -> Credentials:
    key = settings.wiki_ask_api_key
    if key is None or not key.get_secret_value():
        raise AskNotConfigured("Wiki Ask is not configured on this server.")
    return Credentials(values={"api_key": key.get_secret_value()})


def estimate_usd(model: ModelInfo | None, tokens: int) -> float:
    """What ``tokens`` would cost at the model's rates, assuming the split a
    retrieval turn usually has (mostly input). Zero without rates."""
    if model is None:
        return 0.0
    return model.usd_for(int(tokens * 0.8), tokens - int(tokens * 0.8)) or 0.0


def spend_of(result: "TurnResult", model: ModelInfo | None) -> tuple[int, float]:
    """Tokens and USD a finished turn used. USD comes from the configured
    rates so every provider meters alike; the provider's own figure is the
    fallback when a model has no rates."""
    usage = result.usage or {}
    input_tokens = int(usage.get("input_tokens") or 0) + int(
        usage.get("cache_creation_input_tokens") or 0
    ) + int(usage.get("cache_read_input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    tokens = input_tokens + output_tokens
    usd = model.usd_for(input_tokens, output_tokens) if model is not None else None
    if usd is None:
        usd = float(result.cost_usd or 0.0)
    return tokens, usd


async def prepare_ask_turn(
    db: AsyncSession,
    settings: Settings,
    *,
    user_id: str,
    turns_so_far: int,
    wiki: WikiManager,
    earlier: dict[int, dict] | None = None,
) -> tuple[AskContext, Credentials]:
    """Reserve quota and shape the agent for one wiki turn.

    ``earlier`` is the citation numbering the session's previous turns
    handed out (:func:`~app.chat.wiki_mode.earlier_citations`); this turn
    continues it. Raises :class:`AskNotConfigured` without a key and
    :class:`QuotaExceeded` when a cap would be passed; nothing is reserved
    in either case.
    """
    credentials = ask_credentials(settings)
    model = find_model(settings.wiki_ask_provider, settings.wiki_ask_model)
    tokens = settings.wiki_ask_reserve_tokens_per_turn
    reservation = await reserve(
        db, settings,
        user_id=user_id,
        turns_so_far=turns_so_far,
        estimate_tokens=tokens,
        estimate_usd=estimate_usd(model, tokens),
    )
    wiki_turn = WikiTurn(earlier=dict(earlier or {}))
    profile = AgentProfile(
        system_prompt=ASK_SYSTEM_PROMPT,
        allowed_tools=list(ALLOWED_TOOLS),
        mcp_servers={"wiki": build_wiki_tools(wiki, wiki_turn)},
        max_turns=settings.wiki_ask_max_tool_calls,
    )
    return AskContext(profile=profile, wiki_turn=wiki_turn, reservation=reservation, model=model), credentials


def finish_ask_turn(ask: AskContext, result: "TurnResult", text_parts: list[str]) -> None:
    """Assemble the reply, drop citations the session never retrieved, and
    attach this turn's sources plus any earlier ones the reply cites.
    Idempotent."""
    text = "".join(text_parts)
    allowed = ask.wiki_turn.allowed
    filtered = filter_citations(text, allowed)
    if filtered != text:
        logger.info("Wiki Ask reply cited unretrieved sources; dropped them")
    result.assistant_text = filtered
    result.sources = [
        {"n": n, **{k: hit.get(k) for k in ("address", "title", "heading", "link")}}
        for n, hit in sorted(ask.wiki_turn.cited_sources(filtered).items())
    ]

