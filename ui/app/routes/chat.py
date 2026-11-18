"""Chat routes.

Exposes non-streaming turn execution. Streaming (SSE) is layered on top in
step 5; at that point this module grows a second endpoint that shares the
same service layer.
"""

import logging
from typing import Any, Literal

import app.context as ctx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.auth import require_user_api, require_user_page
from app.chat.ask import (
    GENERAL_MODE,
    WIKI_MODE,
    AskContext,
    AskNotConfigured,
    QuotaExceeded,
    prepare_ask_turn,
)
from app.config import get_settings
from app.db.models import BerilUser
from app.routes.context import get_wiki_manager
from app.chat.concurrency import UserChatConcurrencyExceeded, get_concurrency_manager
from app.chat.config import get_chat_config
from app.chat.crud import (
    create_session,
    delete_session,
    get_session_for_user,
    get_session_with_messages,
    list_sessions_for_user,
    update_session,
)
from app.chat.providers import get_provider
from app.chat.providers.base import Credentials
from app.chat.service import run_turn, stream_turn
from app.context import get_base_context
from app.db.models import ChatMessage, ChatSession
from app.db.session import get_db

logger = logging.getLogger(__name__)

ROUTER_CHAT = APIRouter(prefix="/api/chat", tags=["Chat"])
ROUTER_CHAT_PAGES = APIRouter(tags=["Chat"])


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


def _provider_catalog_for_template() -> list[dict]:
    """Serialize the chat config into a list the Jinja template can render.

    Structured so the React component gets the same shape via a JSON island
    later (step 7).
    """
    cfg = get_chat_config()
    return [
        {
            "id": provider_id,
            "display_name": p.display_name,
            "credential_fields": [
                {"id": f.id, "display_name": f.display_name, "secret": f.secret}
                for f in p.credential_fields
            ],
            "models": [{"id": m.id, "display_name": m.display_name} for m in p.models],
        }
        for provider_id, p in cfg.providers.items()
    ]


@ROUTER_CHAT_PAGES.get("/chat", response_class=HTMLResponse)
async def chat_list_page(
    request: Request,
    beril_user: BerilUser = Depends(require_user_page),
    context: dict = Depends(get_base_context),
    db: AsyncSession = Depends(get_db),
):
    """List the user's chat sessions."""
    context["active_sessions"] = await list_sessions_for_user(
        db, beril_user.id, include_archived=False
    )
    context["archived_sessions"] = [
        s
        for s in await list_sessions_for_user(
            db, beril_user.id, include_archived=True
        )
        if s.archived
    ]
    context["providers"] = _provider_catalog_for_template()
    return ctx.templates.TemplateResponse(request, "chat/list.html", context)


@ROUTER_CHAT_PAGES.get("/chat/{session_id}", response_class=HTMLResponse)
async def chat_session_page(
    session_id: str,
    request: Request,
    beril_user: BerilUser = Depends(require_user_page),
    context: dict = Depends(get_base_context),
    db: AsyncSession = Depends(get_db),
):
    """Render a single chat session with its transcript."""
    session = await get_session_with_messages(db, session_id)
    if session is None or session.owner_id != beril_user.id:
        return ctx.templates.TemplateResponse(
            request, "error.html", {**context, "status_code": 404}, status_code=404
        )

    context["session"] = session
    context["messages"] = session.messages
    context["messages_json"] = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content or {},
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in session.messages
    ]
    context["providers"] = _provider_catalog_for_template()
    return ctx.templates.TemplateResponse(request, "chat/session.html", context)


class TurnRequest(BaseModel):
    """JSON body for POST /api/chat/{session_id}/turn."""

    message: str = Field(min_length=1)
    # Credentials: {credential_field_id: value}. Keys must match the provider
    # config's credential_fields[*].id (e.g. "api_key"). Never logged.
    credentials: dict[str, str] = Field(default_factory=dict)


def _validate_credentials(provider_id: str, provided: dict[str, str]) -> Credentials:
    provider = get_provider(provider_id)
    missing = [
        f.id for f in provider.config.credential_fields if not provided.get(f.id)
    ]
    if missing:
        raise ValueError(f"missing credentials: {', '.join(missing)}")
    return Credentials(values=provided)


ASK_NOT_CONFIGURED = "Wiki Ask is not configured on this server."


async def _prepare_turn(
    db: AsyncSession, session: ChatSession, user: BerilUser, body: "TurnRequest"
) -> tuple[Credentials, AskContext | None] | JSONResponse:
    """Credentials and, in wiki mode, the Ask context for one turn.

    General mode validates the user's own credentials. Wiki mode ignores
    them: the key is the admin's (settings), and the turn is refused with a
    429 naming the cap and when it resets, or a 503 when Ask is not
    configured.
    """
    if session.mode != WIKI_MODE:
        try:
            return _validate_credentials(session.provider_id, body.credentials), None
        except (KeyError, ValueError) as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
    turns = (
        await db.execute(
            select(func.count()).select_from(ChatMessage).where(
                ChatMessage.session_id == session.id, ChatMessage.role == "assistant"
            )
        )
    ).scalar_one()
    try:
        ask, credentials = await prepare_ask_turn(
            db, get_settings(), user_id=user.id, turns_so_far=turns, wiki=get_wiki_manager()
        )
    except AskNotConfigured:
        return JSONResponse({"error": ASK_NOT_CONFIGURED}, status_code=503)
    except QuotaExceeded as exc:
        return JSONResponse(
            {"error": exc.detail, "cap": exc.cap, "resets_at": exc.resets_at.isoformat()},
            status_code=429,
        )
    return credentials, ask


async def _load_session_for_user(
    db: AsyncSession, session_id: str, user_id: str
) -> tuple[ChatSession | None, int | None]:
    """Return (session, None) on success, or (None, http_status_code) on auth failure."""
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        return None, 404
    if session.owner_id != user_id:
        return None, 403
    return session, None


@ROUTER_CHAT.post("/{session_id}/turn")
async def chat_turn(
    session_id: str,
    body: TurnRequest,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Run one chat turn to completion and return the assistant's response.

    Non-streaming. Returns JSON on both success and provider error. The
    streaming variant lives at ``.../stream``.
    """
    session, err = await _load_session_for_user(db, session_id, user.id)
    if err is not None or session is None:
        return Response(status_code=err)

    manager = get_concurrency_manager()
    try:
        # Admit the turn before preparing it: in wiki mode preparing reserves
        # quota, which a refused turn would otherwise keep.
        async with manager.acquire(session_id=session.id, user_id=user.id):
            # Refresh after acquiring the lock so we see any sdk_session_id
            # written by a turn that just finished on this same session.
            await db.refresh(session)
            prepared = await _prepare_turn(db, session, user, body)
            if isinstance(prepared, JSONResponse):
                return prepared
            credentials, ask = prepared
            try:
                turn = await run_turn(
                    db,
                    session=session,
                    user_message=body.message,
                    credentials=credentials,
                    ask=ask,
                )
            finally:
                if ask is not None:
                    await ask.release(db)
    except UserChatConcurrencyExceeded:
        return JSONResponse(
            {"error": "concurrent-turn cap exceeded for this user"},
            status_code=429,
        )

    payload: dict[str, Any] = {
        "session_id": session.id,
        "assistant_text": turn.assistant_text,
        "tool_activity": turn.tool_activity,
    }
    if ask is not None:
        payload["sources"] = turn.sources
    if turn.is_error:
        payload["error"] = turn.error
    return JSONResponse(payload)


@ROUTER_CHAT.post("/{session_id}/stream")
async def chat_stream(
    session_id: str,
    body: TurnRequest,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Run one chat turn and stream events to the browser as SSE.

    Pre-flight (auth, ownership, credential validation, concurrency cap) runs
    synchronously and can return a plain JSON error response. Once the SSE
    stream has started, errors surface as ``error`` events inside the stream.
    """
    session, err = await _load_session_for_user(db, session_id, user.id)
    if err is not None:
        return Response(status_code=err)
    assert session is not None

    manager = get_concurrency_manager()
    # Reserve the user slot and session lock BEFORE returning the response,
    # so a cap-exceeded case surfaces as a plain 429 rather than an opaque
    # 200 with an embedded error frame — and before preparing the turn, whose
    # quota reservation (wiki mode) a refused turn would otherwise keep.
    try:
        turn_guard = manager.acquire(session_id=session.id, user_id=user.id)
        await turn_guard.__aenter__()
    except UserChatConcurrencyExceeded:
        return JSONResponse(
            {"error": "concurrent-turn cap exceeded for this user"},
            status_code=429,
        )

    # Anything between acquire and handoff to EventSourceResponse must
    # release the guard manually; only the generator's finally fires once
    # streaming starts.
    try:
        # Refresh after acquiring the lock so we see any sdk_session_id
        # written by a turn that just finished on this same session.
        await db.refresh(session)
        prepared = await _prepare_turn(db, session, user, body)
    except BaseException:
        await turn_guard.__aexit__(None, None, None)
        raise
    if isinstance(prepared, JSONResponse):
        await turn_guard.__aexit__(None, None, None)
        return prepared
    credentials, ask = prepared

    async def _event_generator():
        try:
            async for frame in stream_turn(
                db,
                session=session,
                user_message=body.message,
                credentials=credentials,
                ask=ask,
            ):
                yield frame
        finally:
            try:
                if ask is not None:
                    await ask.release(db)
            finally:
                await turn_guard.__aexit__(None, None, None)

    return EventSourceResponse(_event_generator())


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------


class CreateSessionRequest(BaseModel):
    # ``general`` needs a provider and model of the user's choosing; ``wiki``
    # (Ask over the wiki, on the admin-held key) takes them from settings.
    mode: Literal["general", "wiki"] = GENERAL_MODE
    provider_id: str | None = Field(default=None, min_length=1)
    model: str | None = Field(default=None, min_length=1)
    title: str | None = Field(default=None, max_length=500)


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    archived: bool | None = None


def _validate_provider_and_model(provider_id: str, model: str) -> str | None:
    """Return an error message if the provider or model isn't configured."""
    try:
        provider = get_provider(provider_id)
    except KeyError:
        return f"unknown provider {provider_id!r}"
    if not any(m.id == model for m in provider.config.models):
        return f"unknown model {model!r} for provider {provider_id!r}"
    return None


@ROUTER_CHAT.post("")
async def chat_create_session(
    body: CreateSessionRequest,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Create a new chat session. Returns ``{session_id}`` for client redirect.

    A ``wiki`` session runs on ``BERIL_WIKI_ASK_PROVIDER`` / ``_MODEL``; a
    provider or model in the body is ignored for it. 503 when Ask has no key.
    """
    if body.mode == WIKI_MODE:
        settings = get_settings()
        if settings.wiki_ask_api_key is None or not settings.wiki_ask_api_key.get_secret_value():
            return JSONResponse({"error": ASK_NOT_CONFIGURED}, status_code=503)
        provider_id, model = settings.wiki_ask_provider, settings.wiki_ask_model
    else:
        if not body.provider_id or not body.model:
            return JSONResponse({"error": "provider_id and model are required"}, status_code=400)
        provider_id, model = body.provider_id, body.model
    err = _validate_provider_and_model(provider_id, model)
    if err:
        return JSONResponse({"error": err}, status_code=400)

    session = await create_session(
        db,
        owner_id=user.id,
        provider_id=provider_id,
        model=model,
        title=body.title or ("Ask the wiki" if body.mode == WIKI_MODE else "New chat"),
        mode=body.mode,
    )
    return JSONResponse({"session_id": session.id, "mode": session.mode})


@ROUTER_CHAT.patch("/{session_id}")
async def chat_update_session(
    session_id: str,
    body: UpdateSessionRequest,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Rename, archive, or unarchive a chat session."""
    session = await get_session_for_user(db, session_id, user.id)
    if session is None:
        # Don't leak the difference between "doesn't exist" and "not yours".
        return Response(status_code=404)

    if body.title is None and body.archived is None:
        return JSONResponse({"error": "no fields to update"}, status_code=400)

    await update_session(db, session, title=body.title, archived=body.archived)
    return JSONResponse(
        {
            "session_id": session.id,
            "title": session.title,
            "archived": session.archived,
        }
    )


@ROUTER_CHAT.delete("/{session_id}")
async def chat_delete_session(
    session_id: str,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Hard-delete a chat session and its messages."""
    session = await get_session_for_user(db, session_id, user.id)
    if session is None:
        return Response(status_code=404)

    await delete_session(db, session)
    return Response(status_code=204)
