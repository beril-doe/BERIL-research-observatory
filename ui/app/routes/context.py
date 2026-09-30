"""Routes abstracting an LLM context manager

This puts any context manager queries - i.e. to OpenViking - behind a common API so
the user / consumer doesn't need to know any details.

This provides a mechanism to query the context manager RAG db with a reasonably
simple API. It also provides API calls for the user / agent to manage their data
within BERIL's context manager implementation.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import BerilUser, require_user_api
from app.config import get_settings
from app.context_manager.openviking import (
    ContextQuery,
    OpenVikingManager,
    OvProvisioningError,
    UnauthenticatedError,
    get_user_ov_api_key,
)
from app.db.session import get_db

logger = logging.getLogger()

def get_context_manager(api_key: str) -> OpenVikingManager:
    return OpenVikingManager(get_settings(), api_key)


async def resolve_context_manager(
    db: AsyncSession, user: BerilUser
) -> OpenVikingManager:
    """Build a context manager for ``user``, provisioning their backing
    credential on first use.

    The backing store is an implementation detail, so its failures surface as
    a generic 502 rather than anything the user is expected to act on.
    """
    try:
        api_key = await get_user_ov_api_key(db, user)
    except UnauthenticatedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
    except OvProvisioningError as exc:
        logger.warning("Context manager unavailable for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The context manager is currently unavailable.",
        ) from exc
    return get_context_manager(api_key)


ROUTER_CONTEXT = APIRouter(tags=["context"])

@ROUTER_CONTEXT.post("/api/context/find")
async def post_context_find(
    query: ContextQuery,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Running context query: {query}")
    manager = await resolve_context_manager(db, user)
    return await manager.query(query)

@ROUTER_CONTEXT.get("/api/context/ls")
async def get_context_files(
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    manager = await resolve_context_manager(db, user)
    return await manager.list_files()
