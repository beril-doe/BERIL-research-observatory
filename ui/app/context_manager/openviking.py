import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.openviking import (
    OpenVikingClient,
    OpenVikingError,
    regenerate_ov_user_key,
    register_ov_user,
)
from app.config import Settings, get_settings
from app.crypto import decrypt_secret, encrypt_secret
from app.db.crud import get_ov_credential, upsert_ov_credential
from app.db.models import BerilUser

from .base import (
    ContextFile,
    ContextManager,
    ContextQuery,
    ContextQueryResults,
    QueryResult,
)

logger = logging.getLogger(__name__)


class UnauthenticatedError(RuntimeError):
    """Raised when a context-manager call is made without an identified user."""


class OvProvisioningError(RuntimeError):
    """Raised when a user's OpenViking credential can't be obtained or minted."""


class OpenVikingManager(ContextManager):
    def __init__(self, settings: Settings, api_key: str):
        self.url = settings.ov_url
        self.api_key = api_key

    async def get_file(self, path: Path) -> ContextFile:
        ...

    async def insert_file(self, file: ContextFile) -> bool:
        ...

    async def list_files(self) -> list[ContextFile]:
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        results = await ov_client.list_files("resources/projects")
        await ov_client.close()
        return results

    async def query(self, query: ContextQuery) -> ContextQueryResults:
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        results = await ov_client.find(
            query.query,
            target_uri=query.root_path,
            limit=query.limit,
            score_threshold=query.score_threshold
        )
        processed = ContextQueryResults(
            query=query.query,
            results = [
                QueryResult(
                    uri=r.get("uri"),
                    context_type=r.get("context_type"),
                    score=r.get("score"),
                    text=r.get("abstract")
                ) for r in results.get("resources", [])
            ]
        )
        await ov_client.close()
        return processed

async def get_user_ov_api_key(db: AsyncSession, user: BerilUser) -> str:
    """
    Fetches the OpenViking api key for an authenticated user.
    If user is None or doesn't have an id, raises an UnauthenticatedError.
    If the user has no OpenViking api key, this creates the user in
    OpenViking (and locally) and returns the api key.

    Provisioning is transparent to the caller: the OpenViking account is an
    implementation detail, so a user who already exists upstream but has no key
    stored here is silently issued a fresh one rather than surfacing a conflict.
    That invalidates any prior key for that OV user — acceptable because BERIL
    is the only legitimate holder, and a key BERIL cannot read is unusable here.

    Raises OvProvisioningError if OpenViking is unreachable or returns no key.
    """
    if user is None or not getattr(user, "id", None):
        raise UnauthenticatedError(
            "An authenticated user is required to access OpenViking."
        )

    settings = get_settings()

    existing = await get_ov_credential(db, user.id)
    if existing is not None:
        return decrypt_secret(existing.encrypted_key, settings.ov_credential_key)

    # ov_user_id is always the authenticated user's ORCiD — never caller input.
    ov_user_id = user.orcid_id
    try:
        result = await register_ov_user(ov_user_id)
    except OpenVikingError as exc:
        if exc.status_code != 409 and exc.code != "ALREADY_EXISTS":
            logger.warning("OpenViking register_user failed for %s: %s", user.id, exc)
            raise OvProvisioningError(f"OpenViking user creation failed: {exc}") from exc
        # The OV user outlives BERIL's copy of its key (a dropped credential
        # row, a restored backup, a rotated encryption key). Mint a replacement
        # so the user never has to know OpenViking is involved.
        logger.info(
            "OpenViking user %s exists without a stored BERIL key; regenerating",
            ov_user_id,
        )
        try:
            result = await regenerate_ov_user_key(ov_user_id)
        except OpenVikingError as regen_exc:
            logger.warning(
                "OpenViking regenerate_key failed for %s: %s", user.id, regen_exc
            )
            raise OvProvisioningError(
                f"OpenViking key regeneration failed: {regen_exc}"
            ) from regen_exc

    user_key = (result or {}).get("user_key")
    if not user_key:
        raise OvProvisioningError(
            "OpenViking did not return a user key."
        )

    await upsert_ov_credential(
        db,
        user.id,
        account_id=settings.ov_account_id,
        ov_user_id=ov_user_id,
        encrypted_key=encrypt_secret(user_key, settings.ov_credential_key),
    )
    logger.info(
        "Stored OpenViking credential for BERIL user %s (orcid %s)",
        user.id,
        user.orcid_id,
    )
    return user_key

