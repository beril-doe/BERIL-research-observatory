"""Langfuse ingestion relay.

The Claude Code hooks in ``.claude/hooks/`` trace sessions to a shared Langfuse
Cloud project. Langfuse keys are project-scoped with no write-only variant, so
handing the keypair to every user would let any of them read or delete
everyone's traces. Instead the hooks point the Langfuse SDK at this relay:
``Langfuse(host="<beril>/lf", public_key="beril", secret_key=<BERIL PAT>)``.

The SDK sends HTTP Basic ``public_key:secret_key`` on every call, so the relay
validates the Basic *password* as a BERIL personal access token, swaps in the
server-held project keypair (``settings.langfuse_*``), and forwards the request
verbatim. Only the three write paths the SDK uses are exposed — trace export,
media upload-URL creation, and media finalisation — so the relay is
write-only by construction. The media bytes themselves go from the client to
the presigned storage URL Langfuse returns, never through here.
"""

import base64
import logging

import httpx
from app.auth import BerilUser
from app.config import get_settings
from app.db.crud import get_user_by_api_token
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

ROUTER_LANGFUSE = APIRouter(prefix="/lf/api/public", tags=["langfuse"])

_TIMEOUT = httpx.Timeout(30.0)
# The relay writes with the shared project keys, so bound what one request can
# push. The SDK's OTLP batches are well under this even at the hook's 20k-char
# field cap; media bytes never come through here.
MAX_BODY_BYTES = 16 * 1024 * 1024
# Request headers copied upstream. Everything else (Host, Authorization, the
# client's x-langfuse-public-key) is dropped or replaced.
_FORWARD_HEADERS = frozenset({"content-type", "content-encoding"})
_FORWARD_PREFIX = "x-langfuse-"


async def require_pat_basic(
    request: Request, db: AsyncSession = Depends(get_db)
) -> BerilUser:
    """Authenticate ``Authorization: Basic <anything>:<BERIL PAT>``.

    The Langfuse SDK only speaks Basic auth, so the personal access token
    travels as the password; the username is ignored.
    """
    header = request.headers.get("Authorization", "")
    token = ""
    if header.lower().startswith("basic "):
        try:
            _, _, token = base64.b64decode(header[6:]).decode().partition(":")
        except (ValueError, UnicodeDecodeError):
            token = ""
    user = await get_user_by_api_token(db, token) if token else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


async def _relay(request: Request, user: BerilUser, path: str) -> Response:
    settings = get_settings()
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Langfuse relay is not configured on this server.",
        )
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() in _FORWARD_HEADERS or k.lower().startswith(_FORWARD_PREFIX)
    }
    headers["x-langfuse-public-key"] = settings.langfuse_public_key
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE)
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE)
    url = f"{settings.langfuse_base_url.rstrip('/')}/api/public/{path}"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            upstream = await client.request(
                request.method,
                url,
                content=body,
                headers=headers,
                auth=(settings.langfuse_public_key, settings.langfuse_secret_key),
            )
    except httpx.HTTPError as exc:
        logger.warning("langfuse relay upstream error for %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Langfuse is unreachable.",
        )
    # Audit line: ties every write to the authenticated BERIL user.
    logger.info(
        "langfuse relay user=%s %s %s -> %d (%d bytes)",
        user.id, request.method, path, upstream.status_code, len(body),
    )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )


@ROUTER_LANGFUSE.post("/otel/v1/traces")
async def relay_traces(request: Request, user: BerilUser = Depends(require_pat_basic)):
    """OTLP span export (the SDK's turn traces)."""
    return await _relay(request, user, "otel/v1/traces")


@ROUTER_LANGFUSE.post("/media")
async def relay_media_create(request: Request, user: BerilUser = Depends(require_pat_basic)):
    """Media record creation; returns Langfuse's presigned upload URL."""
    return await _relay(request, user, "media")


@ROUTER_LANGFUSE.patch("/media/{media_id}")
async def relay_media_patch(
    media_id: str, request: Request, user: BerilUser = Depends(require_pat_basic)
):
    """Media upload finalisation after the client PUT to the presigned URL."""
    return await _relay(request, user, f"media/{media_id}")
