"""Where submitted bytes live: a filesystem tree or an S3 bucket.

Both lay files out as ``<owner>/<project>/<revision>/<path>``, so a revision
is immutable once written and two owners' identically named projects never
collide. Every method is blocking — callers run them in a thread.
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Protocol

from app.config import Settings, get_settings
from app.context_manager.base import ArchiveUnavailableError, ContextFileNotFound

logger = logging.getLogger(__name__)


def object_key(owner: str, project: str, revision: str, path: str) -> str:
    """The store-relative key of one file. ``path`` is already traversal-
    checked by the caller (``parse_address`` / ``_safe_relative_path``)."""
    return f"{owner}/{project}/{revision}/{path.strip('/')}"


class SubmissionStore(Protocol):
    def put(self, owner: str, project: str, revision: str, path: str, data: bytes) -> None: ...

    def get(self, owner: str, project: str, revision: str, path: str) -> bytes:
        """Raises :class:`ContextFileNotFound` when the key is absent."""
        ...

    def exists(self, owner: str, project: str, revision: str, path: str) -> bool: ...


class FilesystemSubmissionStore:
    """Files under ``root``; a put is atomic (temp file, then rename)."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def _path(self, owner: str, project: str, revision: str, path: str) -> Path:
        target = (self.root / object_key(owner, project, revision, path)).resolve()
        # Defense in depth: every segment was checked upstream, but a write
        # must never leave the root whatever reached here.
        if not target.is_relative_to(self.root.resolve()):
            raise ValueError(f"Unsafe store path: {path!r}")
        return target

    def put(self, owner: str, project: str, revision: str, path: str, data: bytes) -> None:
        target = self._path(owner, project, revision, path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".put-")
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
            os.replace(tmp, target)
        except OSError as exc:
            logger.warning("Submission store write failed for %s: %s", target, exc)
            raise ArchiveUnavailableError(f"submission store write failed: {exc}") from exc

    def get(self, owner: str, project: str, revision: str, path: str) -> bytes:
        target = self._path(owner, project, revision, path)
        try:
            return target.read_bytes()
        except FileNotFoundError as exc:
            raise ContextFileNotFound(str(target)) from exc
        except OSError as exc:
            raise ArchiveUnavailableError(f"submission store read failed: {exc}") from exc

    def exists(self, owner: str, project: str, revision: str, path: str) -> bool:
        return self._path(owner, project, revision, path).is_file()

    def remove_revision(self, owner: str, project: str, revision: str) -> None:
        """Drop everything stored for one revision (admin repair only)."""
        shutil.rmtree(self._path(owner, project, revision, "."), ignore_errors=True)


class S3SubmissionStore:
    """Objects under ``s3://<bucket>/<prefix>/``. boto3 is imported lazily so
    the filesystem store never needs it."""

    def __init__(
        self,
        *,
        endpoint_url: str | None,
        bucket: str,
        prefix: str,
        access_key: str | None,
        secret_key: str | None,
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._client = None

    def _key(self, owner: str, project: str, revision: str, path: str) -> str:
        key = object_key(owner, project, revision, path)
        return f"{self.prefix}/{key}" if self.prefix else key

    def _s3(self):
        if self._client is None:
            import boto3

            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
            )
        return self._client

    def put(self, owner: str, project: str, revision: str, path: str, data: bytes) -> None:
        from botocore.exceptions import BotoCoreError, ClientError

        try:
            self._s3().put_object(Bucket=self.bucket, Key=self._key(owner, project, revision, path), Body=data)
        except (ClientError, BotoCoreError) as exc:
            logger.warning("Submission store (S3) write failed: %s", exc)
            raise ArchiveUnavailableError(f"submission store write failed: {exc}") from exc

    def get(self, owner: str, project: str, revision: str, path: str) -> bytes:
        from botocore.exceptions import BotoCoreError, ClientError

        key = self._key(owner, project, revision, path)
        try:
            return self._s3().get_object(Bucket=self.bucket, Key=key)["Body"].read()
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"NoSuchKey", "NotFound", "404"}:
                raise ContextFileNotFound(key) from exc
            raise ArchiveUnavailableError(f"submission store read failed: {code}") from exc
        except BotoCoreError as exc:
            raise ArchiveUnavailableError(f"submission store unreachable: {exc}") from exc

    def exists(self, owner: str, project: str, revision: str, path: str) -> bool:
        from botocore.exceptions import BotoCoreError, ClientError

        try:
            self._s3().head_object(Bucket=self.bucket, Key=self._key(owner, project, revision, path))
            return True
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"NoSuchKey", "NotFound", "404"}:
                return False
            raise ArchiveUnavailableError(f"submission store head failed: {code}") from exc
        except BotoCoreError as exc:
            raise ArchiveUnavailableError(f"submission store unreachable: {exc}") from exc


def build_submission_store(settings: Settings) -> SubmissionStore:
    """The store the settings describe: S3 when a bucket is named, else the
    filesystem directory."""
    if settings.submissions_s3_bucket:
        secret = settings.submissions_s3_secret_key
        return S3SubmissionStore(
            endpoint_url=settings.submissions_s3_endpoint_url,
            bucket=settings.submissions_s3_bucket,
            prefix=settings.submissions_s3_prefix,
            access_key=settings.submissions_s3_access_key,
            secret_key=secret.get_secret_value() if secret is not None else None,
        )
    return FilesystemSubmissionStore(settings.submissions_dir)


_store: SubmissionStore | None = None


def get_submission_store() -> SubmissionStore:
    global _store
    if _store is None:
        _store = build_submission_store(get_settings())
    return _store


def reset_submission_store(store: SubmissionStore | None = None) -> None:
    """Replace (or drop) the cached store. Tests only."""
    global _store
    _store = store
