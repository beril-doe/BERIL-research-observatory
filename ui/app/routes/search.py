"""OpenViking search routes.

A minimal semantic-search surface over the shared BERIL project corpus
(``viking://resources/projects/``). The search runs as the *logged-in user*:
we decrypt their stored OpenViking ``user_key`` and authenticate the query with
it (the same credential path as ``GET /api/ov/credentials``). Every failure
mode returns a clean JSON message rather than a traceback, so the UI can render
a friendly notice — including the case where the user has not provisioned an
OpenViking account yet (``POST /api/ov/user``).

Routes:
  GET /search       — HTML page hosting the React search island
  GET /api/search   — JSON search endpoint the island calls
"""

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

import app.context as ctx
from app.auth import BerilUser, require_user_api, require_user_page
from app.clients.openviking import OpenVikingError, ov_search
from app.config import get_settings
from app.crypto import CredentialEncryptionError, decrypt_secret
from app.db.crud import get_ov_credential
from app.db.session import get_db

logger = logging.getLogger(__name__)

ROUTER_SEARCH = APIRouter(tags=["search"])

# The shared project corpus. Kept local rather than importing from
# observatory_context (the webapp has no dependency on that package today).
RESOURCES_TARGET_URI = "viking://resources/projects/"
DEFAULT_LIMIT = 10
MAX_LIMIT = 50


@ROUTER_SEARCH.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    user: BerilUser = Depends(require_user_page),
    context: dict = Depends(ctx.get_base_context),
):
    """Render the search page. The React island (mounted client-side) owns the
    form and results; this route only serves the SSR shell."""
    return ctx.templates.TemplateResponse(request, "search.html", context)


@ROUTER_SEARCH.get("/api/search")
async def api_search(
    q: str = "",
    limit: int = DEFAULT_LIMIT,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db),
):
    """Run a semantic search as the current user and return trimmed results.

    Success -> ``{query, total, results: [{uri, score, abstract}]}``.
    Any expected failure -> ``{error, message}`` with an appropriate status,
    never a traceback.
    """
    query = (q or "").strip()
    if not query:
        return JSONResponse(
            {"error": "empty_query", "message": "Enter a search term."},
            status_code=400,
        )
    # Clamp the optional max-results into a sane range.
    limit = max(1, min(limit, MAX_LIMIT))

    settings = get_settings()

    cred = await get_ov_credential(db, user.id)
    if cred is None:
        return JSONResponse(
            {
                "error": "no_credential",
                "message": (
                    "You don't have an OpenViking credential yet. "
                    "Set one up from your profile to search."
                ),
            },
            status_code=409,
        )

    try:
        user_key = decrypt_secret(cred.encrypted_key, settings.ov_credential_key)
    except CredentialEncryptionError:
        logger.warning("Failed to decrypt OV credential for user %s", user.id)
        return JSONResponse(
            {
                "error": "decrypt_failed",
                "message": "Your stored credential could not be read. Regenerate it from your profile.",
            },
            status_code=500,
        )

    try:
        result = await ov_search(
            user_key, query, target_uri=RESOURCES_TARGET_URI, limit=limit
        )
    except OpenVikingError as exc:
        if exc.status_code in (401, 403):
            return JSONResponse(
                {
                    "error": "auth_failed",
                    "message": "Your OpenViking key was rejected. Regenerate it from your profile.",
                },
                status_code=502,
            )
        logger.warning("OpenViking search failed for user %s: %s", user.id, exc)
        return JSONResponse(
            {"error": "search_failed", "message": f"Search failed: {exc}"},
            status_code=502,
        )

    resources = (result or {}).get("resources") or []
    return {
        "query": query,
        "total": (result or {}).get("total", len(resources)),
        "results": [
            {
                "uri": r.get("uri", ""),
                "score": r.get("score", 0.0),
                "abstract": r.get("abstract", ""),
            }
            for r in resources
        ],
    }
