"""BERDL lakehouse fallback for reading project files when OpenViking is down.

This is the *middle* tier of the query CLI's degraded path:

    OpenViking (semantic)  →  BERDL lakehouse archive  →  local project files

Projects are archived to the lakehouse object store by ``/submit`` (see
``tools/lakehouse_upload.py``) at ``s3://<bucket>/<tenant>/projects/<id>/...``,
mirroring the local ``projects/`` tree. When OpenViking is unreachable, a
``read``/``overview`` for a project resource can still be served from that
archive — a fresher and more complete source than the local checkout, which may
lag the submitted copy.

Only *direct file fetches* use this tier (``read``, ``overview``). Keyword search
(``find``/``grep``) is not routed here: it would mean downloading the whole
corpus per query, so it drops straight to the local keyword fallback instead.

Any of "no credentials", "endpoint unreachable", "access denied", or "object not
archived" raises :class:`BerdlUnavailable`, which the caller catches to fall
through to the local tier. Nothing here talks to the network at import time.
"""

from __future__ import annotations

from pathlib import Path

from .config import (
    LAKEHOUSE_BUCKET,
    ContextConfig,
    lakehouse_projects_key,
    s3_settings,
)

BANNER = (
    "⚠ knowledge layer unavailable — served from the BERDL lakehouse archive "
    "(submitted copy); it may differ from your local working tree."
)

# S3 error codes that mean "BERDL can't answer this" rather than "unexpected
# bug". AccessDenied → the user lacks permission (still degrade to local);
# NoSuchKey/NoSuchBucket → the project isn't archived (or wrong location).
_UNAVAILABLE_S3_CODES = frozenset(
    {"AccessDenied", "NoSuchKey", "NoSuchBucket", "403", "404"}
)

_RESOURCES_PREFIX = "viking://resources/"
_PROJECTS_PREFIX = f"{_RESOURCES_PREFIX}projects/"


class BerdlUnavailable(Exception):
    """The lakehouse tier cannot serve this request — caller should fall back.

    Raised for missing credentials, an unreachable endpoint, permission
    denial, or a resource that isn't archived. Carries a short human reason so
    the caller can surface *why* it degraded.
    """


def _resolve_credentials() -> dict[str, str | None] | None:
    """Return ``{endpoint_url, access_key, secret_key}`` or ``None`` if unusable.

    Env first (:func:`config.s3_settings`); if keys are absent, try the
    ``berdl-remote`` helper the same way ``scripts/get_minio_creds.py`` does.
    ``None`` means no usable credentials → the tier is unavailable.
    """
    settings = s3_settings()
    if settings["access_key"] and settings["secret_key"]:
        return settings

    remote = _credentials_from_berdl_remote()
    if remote is None:
        return None
    # Keep the resolved endpoint precedence (S3_ENDPOINT_URL/MINIO_ENDPOINT_URL)
    # unless berdl-remote supplied one explicitly.
    return {
        "endpoint_url": remote.get("MINIO_ENDPOINT_URL") or settings["endpoint_url"],
        "access_key": remote.get("MINIO_ACCESS_KEY"),
        "secret_key": remote.get("MINIO_SECRET_KEY"),
    }


def _credentials_from_berdl_remote() -> dict[str, str] | None:
    """Reuse ``get_minio_creds.resolve_from_berdl_remote`` if it is importable.

    The helper lives under ``scripts/`` (not a package), so the import is
    guarded: if it can't be loaded we simply have no remote credentials.
    """
    try:
        import importlib.util

        script = Path(__file__).resolve().parents[1] / "scripts" / "get_minio_creds.py"
        spec = importlib.util.spec_from_file_location("get_minio_creds", script)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except (OSError, ImportError):
        return None
    # bootstrap_remote=False: never spawn a JupyterHub server on a degraded
    # read path — only use creds that are already available.
    return module.resolve_from_berdl_remote(False)


def _s3_client():
    """Build a boto3 S3 client for the lakehouse, or raise ``BerdlUnavailable``.

    ``boto3`` is an optional dependency (``knowledge`` group). If it or the
    credentials are missing, the tier is unavailable.
    """
    creds = _resolve_credentials()
    if creds is None or not creds["access_key"] or not creds["secret_key"]:
        raise BerdlUnavailable("no S3 credentials for the lakehouse")
    try:
        import boto3
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise BerdlUnavailable("boto3 is not installed") from exc
    return boto3.client(
        "s3",
        endpoint_url=creds["endpoint_url"],
        aws_access_key_id=creds["access_key"],
        aws_secret_access_key=creds["secret_key"],
    )


def uri_to_bucket_key(uri: str) -> tuple[str, str]:
    """Map a project resource URI to an ``(bucket, key)`` in the lakehouse.

    Only ``viking://resources/projects/<id>/<path>`` maps to the archive; docs
    and other resources are not stored there, so they raise
    :class:`BerdlUnavailable` (→ local fallback).
    """
    if not uri.startswith(_PROJECTS_PREFIX):
        raise BerdlUnavailable(f"no lakehouse archive for resource: {uri}")
    rest = uri[len(_PROJECTS_PREFIX):].strip("/")
    if not rest:
        raise BerdlUnavailable("cannot resolve the projects root to a single object")
    parts = rest.split("/", 1)
    project_id = parts[0]
    rel_path = parts[1] if len(parts) > 1 else ""
    return LAKEHOUSE_BUCKET, lakehouse_projects_key(project_id, rel_path)


def _get_object_text(client, bucket: str, key: str) -> str:
    """Fetch an object's UTF-8 body, translating S3 failures to unavailability."""
    try:
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise BerdlUnavailable("botocore is not installed") from exc
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read().decode("utf-8", errors="replace")
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code in _UNAVAILABLE_S3_CODES:
            raise BerdlUnavailable(f"lakehouse {code} for {key}") from exc
        raise BerdlUnavailable(f"lakehouse error for {key}: {code}") from exc
    except BotoCoreError as exc:  # endpoint unreachable, connection error, etc.
        raise BerdlUnavailable(f"lakehouse unreachable: {exc}") from exc


def berdl_available(config: ContextConfig) -> bool:
    """Cheap probe: can we reach the lakehouse and are we authorized?

    Lists a single object under the projects prefix. Returns ``False`` on any
    credential/reachability/permission problem, without raising — parallel to
    ``openviking_client.server_reachable``.
    """
    try:
        client = _s3_client()
        from botocore.exceptions import BotoCoreError, ClientError
    except (BerdlUnavailable, ImportError):
        return False
    try:
        client.list_objects_v2(
            Bucket=LAKEHOUSE_BUCKET,
            Prefix=lakehouse_projects_key("", ""),
            MaxKeys=1,
        )
        return True
    except (ClientError, BotoCoreError):
        return False


def berdl_read(config: ContextConfig, uri: str) -> str:
    """Read a project resource from the lakehouse archive.

    Raises :class:`BerdlUnavailable` if the tier can't serve it (no creds,
    unreachable, unauthorized, or not archived).
    """
    bucket, key = uri_to_bucket_key(uri)
    client = _s3_client()
    return _get_object_text(client, bucket, key)


def berdl_overview(config: ContextConfig, uri: str) -> str:
    """Overview of a project resource from the lakehouse.

    For a project directory URI (``.../projects/<id>/``) this returns the first
    lines of its archived ``README.md``, mirroring the local overview. For a
    file URI it returns the file's content.
    """
    bucket, key = uri_to_bucket_key(uri)
    client = _s3_client()
    # Directory form (``.../projects/<id>/``) overviews the archived README;
    # a file URI returns the file itself. `key` never has a trailing slash.
    if uri.endswith("/"):
        text = _get_object_text(client, bucket, f"{key}/README.md")
        return "\n".join(text.splitlines()[:40])
    return _get_object_text(client, bucket, key)
