"""Application configuration."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_settings = None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Test-only settings. These should be left False unless running tests.
    test_skip_lifespan: bool = False

    # Image info. Only used for health endpoint when present
    git_commit: str | None = None
    build_date: str | None = None

    # Paths
    app_dir: Path = Path(__file__).parent
    ui_dir: Path = app_dir.parent
    repo_dir: Path = ui_dir.parent  # The research repository root

    # Git data source configuration
    data_repo_url: str | None = None  # Git repository URL
    data_repo_branch: str = "data-cache"  # Branch to checkout
    data_repo_path: Path = Path("/tmp/beril_data_cache")  # Local clone path
    force_local_data: bool = False

    plotly_cdn_url: str = "https://cdn.plot.ly/plotly-3.4.0.min.js"

    # Webhook configuration
    webhook_secret: str | None = None

    # ORCiD OAuth2 configuration
    orcid_client_id: str | None = None
    orcid_client_secret: str | None = None
    orcid_redirect_root: str = "http://localhost:8000"  # expected not to end with a slash
    orcid_redirect_path: str = "/auth/orcid/callback"  # expects to be prepended with slash
    orcid_base_url: str = "https://orcid.org"  # Use https://sandbox.orcid.org for development

    # Auth token providers — comma-separated names of TokenProvider plugins to
    # enable in addition to ORCiD identity. Currently only "kbase" is supported.
    # Empty by default, so dev deployments get ORCiD-only behavior.
    auth_token_providers: str = ""

    # Name of the cookie KBase auth writes to the shared *.kbase.us domain.
    # Read on every request by KBaseTokenProvider when the provider is enabled.
    kbase_auth_cookie: str = "kbase_session_backup"
    kbase_auth_url: str = "https://ci.kbase.us/services/auth"
    kbase_auth_mfa: bool = True

    # Session configuration
    session_secret_key: str = "change-me-in-production"  # Signs session cookies

    # database info
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "beril_user"
    db_password: str | None = None
    db_name: str = "beril"

    # User project file storage (filesystem)
    user_projects_root: Path = ui_dir / "user_projects"

    # Chat configuration
    chat_config_path: Path = ui_dir / "config" / "chat_providers.yaml"
    chat_max_concurrent_turns_per_user: int = 3

    # OpenViking configuration
    ov_url: str = "http://localhost:1933"
    ov_account_id: str = "beril"
    ov_account_admin: str = "beril_admin"
    ov_admin_key: str = "change-me-in-production"
    # Fernet key for encrypting OpenViking user credentials at rest.
    # urlsafe-base64-encoded 32-byte key; generate with Fernet.generate_key().
    ov_credential_key: str | None = None

    # Context-manager ingest limits. Each file is spilled to a temp file before
    # being handed to the context manager, so an uncapped batch would tie up
    # local disk and the backend's processing queue.
    context_max_ingest_files: int = 50
    context_max_file_bytes: int = 50 * 1024 * 1024
    # The upload as sent (compressed), the manifest, and the archive's total
    # expanded size. Checked before anything is extracted; the proxy's body
    # limit (nginx client_max_body_size, ingress proxy-body-size) must be at
    # least the archive cap plus multipart overhead.
    context_max_archive_bytes: int = 32 * 1024 * 1024
    context_max_manifest_bytes: int = 1024 * 1024
    context_max_expanded_bytes: int = 128 * 1024 * 1024
    # Entries in the archive's central directory, all of them — not just the
    # ones the manifest names. Read from the end-of-central-directory record
    # before the directory is parsed, so a flood of tiny unlisted entries is
    # refused without being materialized. The mirror sends tens of files.
    context_max_archive_entries: int = 1000

    # Langfuse relay (app/routes/langfuse.py): the shared project keypair lives
    # only here. Leave the keys unset to disable the relay (503).
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str = "https://us.cloud.langfuse.com"

    # Lakehouse archive (app/clients/archive.py): the copy of every submitted
    # project that ``/submit`` writes to object storage, read by
    # ``GET /api/context/read`` when the context store's copy is not
    # byte-exact or the path was never ingested (figures). S3-compatible;
    # MinIO today, Ceph RGW later — the endpoint is config, not code. Leave
    # the keys unset and the archive is simply unavailable (such reads 502).
    # Objects live at ``s3://<bucket>/<prefix>/<project>/<path>``.
    archive_endpoint_url: str = "https://minio.berdl.kbase.us"
    archive_bucket: str = "cdm-lake"
    archive_prefix: str = "tenant-general-warehouse/microbialdiscoveryforge/projects"
    archive_access_key: str | None = None
    archive_secret_key: SecretStr | None = None
    archive_timeout_seconds: float = 20.0

    # Wiki Ask: the conversational agent over the wiki corpus, run on an
    # admin-held provider key rather than the reader's. Every limit lives here
    # so it can be tuned per deployment once real usage is known; nothing in
    # the chat code may hard-code these. The provider names an entry in
    # ``chat_providers.yaml``; the model is one of that provider's. Quotas
    # count tokens (input plus output) per calendar day per user, and per
    # calendar month across every user; ``max_turns`` bounds one
    # conversation and ``max_tool_calls`` one turn's calls to the wiki's tool
    # server. The key unset means Ask is off.
    wiki_ask_provider: str = "anthropic"
    wiki_ask_model: str = "claude-sonnet-4-6"
    wiki_ask_api_key: SecretStr | None = None
    wiki_ask_daily_tokens_per_user: int = 250_000
    wiki_ask_monthly_tokens: int = 25_000_000
    wiki_ask_max_turns: int = 20
    wiki_ask_max_tool_calls: int = 8

    # Derived paths
    @property
    def db_url(self) -> str:
        if self.db_password is None:
            raise ValueError("BERIL_DB_PASSWORD is not set — cannot construct database URL")
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def require_ov_credential_key(self) -> str:
        """The Fernet key, or a startup-time error if it is not configured.

        Without it every stored context credential is unreadable and every
        new one unwritable, so each context request would 500. That is a
        deployment mistake, not a runtime condition — fail once, loudly, at
        startup, the way ``db_url`` does for a missing database password.
        """
        if not self.ov_credential_key:
            raise ValueError(
                "BERIL_OV_CREDENTIAL_KEY is not set — context credentials cannot "
                "be stored or read. Generate one with Fernet.generate_key()."
            )
        # Set but malformed is the same deployment mistake, and a worse one if
        # it reaches runtime: every stored credential would read as corrupt.
        # Imported here so config stays importable without the crypto stack.
        from app.crypto import InvalidEncryptionKeyError, validate_key

        try:
            validate_key(self.ov_credential_key)
        except InvalidEncryptionKeyError as exc:
            raise ValueError(
                "BERIL_OV_CREDENTIAL_KEY is not a valid Fernet key (expected "
                "urlsafe-base64-encoded 32 bytes). Generate one with "
                "Fernet.generate_key()."
            ) from exc
        return self.ov_credential_key

    @property
    def orcid_redirect_uri(self) -> str:
        return self.orcid_redirect_root + self.orcid_redirect_path

    @property
    def auth_token_providers_list(self) -> list[str]:
        return [p.strip() for p in self.auth_token_providers.split(",") if p.strip()]

    @property
    def projects_dir(self) -> Path:
        return self.repo_dir / "projects"

    @property
    def docs_dir(self) -> Path:
        return self.repo_dir / "docs"

    @property
    def data_dir(self) -> Path:
        return self.repo_dir / "data"

    @property
    def templates_dir(self) -> Path:
        return self.app_dir / "templates"

    @property
    def static_dir(self) -> Path:
        return self.app_dir / "static"

    @property
    def cache_dir(self) -> Path:
        return self.ui_dir / "data"

    @property
    def cache_file(self) -> Path:
        return self.cache_dir / "cache.json"

    @property
    def search_index_dir(self) -> Path:
        return self.cache_dir / "indexdir"

    # App settings
    app_name: str = "Microbial Discovery Forge"
    app_description: str = (
        "AI co-scientist and research observatory for BERDL-scale microbial discovery"
    )
    debug: bool = False

    # Database stats (for hero display)
    total_genomes: int = 293_059
    total_species: int = 27_000
    total_genes: str = "1B+"

    model_config = SettingsConfigDict(
        env_prefix="BERIL_",  # BERIL Research Observatory
        # Resolve .env relative to the repo root (two levels up from this file)
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        # pydantic-settings 2.x defaults to "forbid"; the repo's .env contains
        # non-BERIL_ vars (KBASE_AUTH_TOKEN, JLAB_API_TOKEN, etc.) that are not
        # part of the app settings and must be ignored.
        extra="ignore",
    )


def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
