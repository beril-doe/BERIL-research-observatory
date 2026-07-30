from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OPENVIKING_URL = "http://127.0.0.1:1933"
PROJECTS_TARGET_URI = "viking://resources/projects/"
DOCS_TARGET_URI = "viking://resources/docs/"

# --- BERDL lakehouse object storage --------------------------------------
#
# Location of the project archive in the lakehouse object store. Projects are
# uploaded here by ``/submit`` (via ``tools/lakehouse_upload.py``) and read back
# by the BERDL fallback tier (``observatory_context.berdl_fallback``) when
# OpenViking is unavailable.
#
# TODO(consolidation): ``tools/lakehouse_upload.py`` still defines its own copies
# of BUCKET / TENANT_PATH (as ``mc``-alias + ``s3a://`` path bases). These values
# MUST stay in sync with the ones here. Fold that script onto these constants —
# it needs a ``sys.path`` shim first (it is run as a bare cwd-relative script by
# ``/submit`` with no import root) and must preserve its ``--tenant-path`` runtime
# override. See memory ``project_lakehouse_config_consolidation``.
LAKEHOUSE_BUCKET = "cdm-lake"
LAKEHOUSE_TENANT_PATH = "tenant-general-warehouse/microbialdiscoveryforge"
LAKEHOUSE_PROJECTS_PREFIX = "projects"

# Default S3 endpoint for the object store. MinIO today; the lakehouse is moving
# to Ceph (RADOS Gateway), which speaks the same S3 API — so the endpoint is
# resolved from the environment (``S3_ENDPOINT_URL`` first, then the legacy
# ``MINIO_ENDPOINT_URL``) and the Ceph cutover is an env change, not a code edit.
DEFAULT_S3_ENDPOINT_URL = "https://minio.berdl.kbase.us"


def lakehouse_projects_key(
    project_id: str,
    rel_path: str = "",
    *,
    tenant_path: str = LAKEHOUSE_TENANT_PATH,
) -> str:
    """Return the S3 object key (no bucket) for a file in a project's archive.

    ``tenant/projects/<project_id>/<rel_path>``. With no ``rel_path`` this is the
    project's archive prefix (no trailing slash). Used to translate a
    ``viking://resources/projects/...`` URI into a boto3 ``(bucket, key)`` pair.
    """
    base = f"{tenant_path}/{LAKEHOUSE_PROJECTS_PREFIX}/{project_id}"
    rel = rel_path.strip("/")
    return f"{base}/{rel}" if rel else base


def s3_settings() -> dict[str, str | None]:
    """Resolve S3 endpoint + credentials for the object store from the env.

    Endpoint precedence: ``S3_ENDPOINT_URL`` (Ceph-ready) → ``MINIO_ENDPOINT_URL``
    (legacy) → :data:`DEFAULT_S3_ENDPOINT_URL`. Keys come from
    ``MINIO_ACCESS_KEY`` / ``MINIO_SECRET_KEY`` and may be ``None`` (caller then
    falls back to ``berdl-remote`` or treats the tier as unavailable).
    """
    endpoint = (
        os.getenv("S3_ENDPOINT_URL")
        or os.getenv("MINIO_ENDPOINT_URL")
        or DEFAULT_S3_ENDPOINT_URL
    )
    return {
        "endpoint_url": endpoint,
        "access_key": os.getenv("MINIO_ACCESS_KEY"),
        "secret_key": os.getenv("MINIO_SECRET_KEY"),
    }


def _cached_ov_credential() -> tuple[str | None, str | None]:
    """Return ``(ov_url, ov_user_key)`` cached by ``beril login`` / ``beril ov``.

    Reads ~/.beril/auth.json via ``beril_cli.auth_store``. The import is guarded
    so ``observatory_context`` keeps working in environments where ``beril_cli``
    isn't on the path (returns ``(None, None)`` — same as no cached credential).
    """
    try:
        from beril_cli import auth_store
    except ImportError:
        return (None, None)
    creds = auth_store.load_ov()
    if creds is None:
        return (None, None)
    return creds


@dataclass(frozen=True)
class ContextConfig:
    repo_root: Path
    openviking_url: str = DEFAULT_OPENVIKING_URL
    openviking_api_key: str | None = None

    @classmethod
    def from_env(cls, repo_root: Path | None = None) -> "ContextConfig":
        root = repo_root or Path(__file__).resolve().parents[1]

        # Precedence: explicit env vars win (CI, `--env-file .env`, manual
        # export), then fall back to the credential `beril login` / `beril ov
        # setup` cached in ~/.beril. This lets the query CLI work with no
        # env-file once the user has logged in.
        url = os.getenv("OPENVIKING_URL")
        key = os.getenv("OPENVIKING_API_KEY")
        if not url or not key:
            cached_url, cached_key = _cached_ov_credential()
            url = url or cached_url
            key = key or cached_key

        return cls(
            repo_root=root,
            openviking_url=url or DEFAULT_OPENVIKING_URL,
            openviking_api_key=key,
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "repo_root", Path(self.repo_root))

    @property
    def projects_dir(self) -> Path:
        return self.repo_root / "projects"

    @property
    def docs_dir(self) -> Path:
        return self.repo_root / "docs"

    @property
    def staging_dir(self) -> Path:
        return self.repo_root / "knowledge" / "staging"

    @property
    def state_dir(self) -> Path:
        return self.repo_root / "knowledge" / "state"
