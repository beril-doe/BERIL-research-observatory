"""User account pages.

Currently only the personal API token management page lives here. The token
page shows the caller's active tokens and lets them create or revoke tokens
for CLI / programmatic access.

The newly-issued raw token is displayed exactly once via a one-shot session
flash: the POST handler stores it under ``_new_token`` and the next GET
pops and renders it. If the user refreshes the page or navigates away, the
raw token is gone — we only ever persist its hash.
"""

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

import app.context as ctx
from app.auth import require_user_page
from app.context import get_base_context
from app.db.crud import (
    create_named_api_token,
    list_api_tokens_for_user,
    revoke_api_token,
)
from app.db.models import BerilUser
from app.db.session import get_db

logger = logging.getLogger(__name__)

ROUTER_USER_ACCOUNT = APIRouter(tags=["Account"])


# Expiry options exposed in the create form. Kept small on purpose — power
# users who want unusual expiries can extend the enum later.
EXPIRY_CHOICES: dict[str, int | None] = {
    "30": 30,
    "90": 90,
    "180": 180,
    "365": 365,
    "never": None,
}


@ROUTER_USER_ACCOUNT.get("/account/tokens", response_class=HTMLResponse)
async def account_tokens_page(
    request: Request,
    user: BerilUser = Depends(require_user_page),
    context: dict = Depends(get_base_context),
    db: AsyncSession = Depends(get_db),
):
    """List the caller's active API tokens; show a just-created token once."""
    tokens = await list_api_tokens_for_user(db, user.id)
    # One-shot flash: pop so a refresh doesn't re-display the raw token.
    new_token = request.session.pop("_new_token", None)
    context["tokens"] = tokens
    context["new_token"] = new_token
    context["expiry_choices"] = list(EXPIRY_CHOICES.keys())
    return ctx.templates.TemplateResponse(request, "account/tokens.html", context)


@ROUTER_USER_ACCOUNT.post("/account/tokens")
async def account_tokens_create(
    request: Request,
    name: str = Form(...),
    expires_in: str = Form("365"),
    user: BerilUser = Depends(require_user_page),
    db: AsyncSession = Depends(get_db),
):
    """Create a new named token. Stashes the raw token in a one-shot flash."""
    name = name.strip()
    if not name:
        # Invalid input — silently redirect back. A future iteration can add
        # inline validation messages via the same flash mechanism.
        return RedirectResponse(url="/account/tokens", status_code=302)

    if expires_in not in EXPIRY_CHOICES:
        return RedirectResponse(url="/account/tokens", status_code=302)

    raw_token, record = await create_named_api_token(
        db, user.id, name=name, expires_in_days=EXPIRY_CHOICES[expires_in]
    )
    request.session["_new_token"] = {"raw": raw_token, "name": record.name}
    return RedirectResponse(url="/account/tokens", status_code=302)


@ROUTER_USER_ACCOUNT.post("/account/tokens/{token_id}/revoke")
async def account_tokens_revoke(
    request: Request,
    token_id: str,
    user: BerilUser = Depends(require_user_page),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Revoke one of the caller's tokens. Silently no-ops if not owned —
    we don't leak "this token exists but belongs to someone else"."""
    await revoke_api_token(db, token_id, user.id)
    return RedirectResponse(url="/account/tokens", status_code=302)
