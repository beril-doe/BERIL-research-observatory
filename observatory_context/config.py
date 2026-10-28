from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OPENVIKING_URL = "http://127.0.0.1:1933"
PROJECTS_TARGET_URI = "viking://resources/projects/"

# --- central docs: the house account -------------------------------------
#
# Central docs (pitfalls, discoveries, performance, research_ideas) have no
# owner, but BERIL's read routes address everything as
# ``resources/users/<owner>/…`` — reads span owners, and a submitted project is
# owned by one user and readable by all. Rather than give the ownerless docs a
# special case in every read path, they live under a reserved owner.
#
# Must stay in sync with ``HOUSE_ACCOUNT_ID`` in
# ``ui/app/context_manager/openviking.py``, which reserves the name so no real
# user can claim it. Duplicated rather than imported because this package must
# keep working without the webapp on the path.
HOUSE_ACCOUNT_ID = "beril"
USERS_TARGET_URI = "viking://resources/users/"
DOCS_TARGET_URI = f"{USERS_TARGET_URI}{HOUSE_ACCOUNT_ID}/docs/"
# Where central docs lived before the house account. Retired: nothing writes
# here, and ``--docs`` deletes it as part of the cutover so the old copies do
# not linger as duplicates in search.
LEGACY_DOCS_TARGET_URI = "viking://resources/docs/"

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

    Endpoint and key lookups both prefer the vendor-neutral ``S3_*`` names
    (Ceph-ready) and fall back to the legacy ``MINIO_*`` names, so the Ceph
    cutover is an env change rather than a code edit. Any missing value is
    ``None`` (caller then falls back to ``berdl-remote`` or treats the tier as
    unavailable).
    """
    endpoint = (
        os.getenv("S3_ENDPOINT_URL")
        or os.getenv("MINIO_ENDPOINT_URL")
        or DEFAULT_S3_ENDPOINT_URL
    )
    return {
        "endpoint_url": endpoint,
        "access_key": os.getenv("S3_ACCESS_KEY") or os.getenv("MINIO_ACCESS_KEY"),
        "secret_key": os.getenv("S3_SECRET_KEY") or os.getenv("MINIO_SECRET_KEY"),
    }


@dataclass(frozen=True)
class ContextConfig:
    repo_root: Path
    openviking_url: str = DEFAULT_OPENVIKING_URL
    openviking_api_key: str | None = None

    @classmethod
    def from_env(cls, repo_root: Path | None = None) -> "ContextConfig":
        root = repo_root or Path(__file__).resolve().parents[1]

        # From the environment only (`.env`, CI, a manual export). These tools
        # talk to the store directly, which is an admin's job: users reach the
        # context layer through BERIL (`beril context`) with their BERIL login,
        # and `beril login` no longer caches a store credential to fall back to.
        url = os.getenv("OPENVIKING_URL")
        key = os.getenv("OPENVIKING_API_KEY")

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
