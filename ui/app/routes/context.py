"""Routes abstracting an LLM context manager

This puts any context manager queries - i.e. to OpenViking - behind a common API so
the user / consumer doesn't need to know any details.

This provides a mechanism to query the context manager RAG db with a reasonably
simple API. It also provides API calls for the user / agent to manage their data
within BERIL's context manager implementation.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import BerilUser, require_user_api
from app.config import get_settings
from app.context_manager.openviking import ContextQuery, OpenVikingManager
from app.crypto import decrypt_secret
from app.db.crud import get_ov_credential
from app.db.models import OvUserCredential
from app.db.session import get_db

logger = logging.getLogger()

def get_context_manager(cred: OvUserCredential) -> OpenVikingManager:
    key = get_settings().ov_credential_key
    return OpenVikingManager(get_settings(), decrypt_secret(cred.encrypted_key, key))


ROUTER_CONTEXT = APIRouter(tags=["context"])

@ROUTER_CONTEXT.post("/api/context/find")
async def post_context_find(
    query: ContextQuery,
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Running context query: {query}")
    ov_credential = await get_ov_credential(db, user.id)
    return await get_context_manager(ov_credential).query(query)

@ROUTER_CONTEXT.get("/api/context/ls")
async def get_context_files(
    request: Request,
    user: BerilUser = Depends(require_user_api),
    db: AsyncSession = Depends(get_db)
):
    ov_credential = await get_ov_credential(db, user.id)
    return await get_context_manager(ov_credential).list_files()
