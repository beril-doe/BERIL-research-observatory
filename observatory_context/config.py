from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OPENVIKING_URL = "http://127.0.0.1:1933"
PROJECTS_TARGET_URI = "viking://resources/projects/"
DOCS_TARGET_URI = "viking://resources/docs/"


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
