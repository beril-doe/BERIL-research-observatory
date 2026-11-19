"""The lakehouse archive: the copy of every submitted project that ``/submit``
writes to object storage.

``/submit`` uploads a project's tree to
``s3://<bucket>/<prefix>/<project_id>/<path>`` (``tools/lakehouse_upload.py``)
before it mirrors the curated files into the context store. That copy is the
bytes as submitted — nothing decomposes or re-renders it — so it is the
fallback ``GET /api/context/read`` serves when the store's copy is not
byte-exact, and the only source for files the store never ingests (figures).

Reads only. Settings are ``BERIL_ARCHIVE_*`` (``app.config``); without
credentials the archive is unavailable, which callers report as a 502 rather
than a missing file. boto3's client is synchronous, so callers run
:meth:`LakehouseArchive.get` in a thread.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from app.config import Settings
from app.context_manager.base import ArchiveUnavailableError, ContextFileNotFound

logger = logging.getLogger(__name__)

# S3 error codes that mean "no such object" rather than "could not ask".
_NOT_FOUND_CODES = frozenset({"NoSuchKey", "NotFound", "404"})


@dataclass(frozen=True)
class ArchivedObject:
    """One object's bytes and the metadata the store reports for it."""

    data: bytes
    content_type: str | None
    last_modified: datetime | None


class LakehouseArchive:
    """Reader for one project archive location (bucket + prefix)."""

    def __init__(
        self,
        *,
        endpoint_url: str,
        bucket: str,
        prefix: str,
        access_key: str | None,
        secret_key: str | None,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self._access_key = access_key
        self._secret_key = secret_key
        self._timeout = timeout_seconds
        self._client = None

    @classmethod
    def from_settings(cls, settings: Settings) -> "LakehouseArchive":
        secret = settings.archive_secret_key
        return cls(
            endpoint_url=settings.archive_endpoint_url,
            bucket=settings.archive_bucket,
            prefix=settings.archive_prefix,
            access_key=settings.archive_access_key,
            secret_key=secret.get_secret_value() if secret is not None else None,
            timeout_seconds=settings.archive_timeout_seconds,
        )

    @property
    def configured(self) -> bool:
        return bool(self._access_key and self._secret_key)

    def key_for(self, project: str, path: str) -> str:
        """The object key of ``path`` within ``project``'s archive.

        ``project`` is the project's slug — the directory name under
        ``projects/`` that ``/submit`` archived it as — and ``path`` is
        already traversal-checked by the caller.
        """
        return f"{self.prefix}/{project}/{path.strip('/')}"

    def _s3(self):
        if self._client is None:
            if not self.configured:
                raise ArchiveUnavailableError(
                    "The lakehouse archive has no credentials (BERIL_ARCHIVE_ACCESS_KEY / "
                    "BERIL_ARCHIVE_SECRET_KEY)."
                )
            # Imported here so the app imports without boto3 on the path and
            # a misconfigured archive fails at the first read, not at startup.
            import boto3
            from botocore.config import Config

            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                config=Config(
                    connect_timeout=self._timeout,
                    read_timeout=self._timeout,
                    retries={"max_attempts": 2},
                ),
            )
        return self._client

    def get(self, project: str, path: str) -> ArchivedObject:
        """Fetch one archived file. Blocking — run it in a thread.

        Raises :class:`ContextFileNotFound` when the object is not there, and
        :class:`ArchiveUnavailableError` for anything that means the archive
        could not be asked (no credentials, unreachable, refused).
        """
        key = self.key_for(project, path)
        client = self._s3()
        from botocore.exceptions import BotoCoreError, ClientError

        try:
            response = client.get_object(Bucket=self.bucket, Key=key)
            data = response["Body"].read()
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in _NOT_FOUND_CODES:
                raise ContextFileNotFound(f"not archived: {key}") from exc
            # The code is logged, not returned: AccessDenied and friends are
            # a deployment problem, and the caller reports them all as 502.
            logger.warning("Lakehouse archive refused %s: %s", key, code or exc)
            raise ArchiveUnavailableError(f"lakehouse error for {key}: {code}") from exc
        except BotoCoreError as exc:
            logger.warning("Lakehouse archive unreachable for %s: %s", key, exc)
            raise ArchiveUnavailableError(f"lakehouse unreachable: {exc}") from exc
        return ArchivedObject(
            data=data,
            content_type=response.get("ContentType"),
            last_modified=response.get("LastModified"),
        )
