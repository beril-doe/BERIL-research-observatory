"""The wiki as a second context backend.

The wiki container exposes an internal, token-guarded API under
``/wiki/_api/`` (search, read, ls, source), reachable only in-cluster.
:class:`WikiManager` puts it behind the same ``find`` / ``read`` / ``ls``
routes as the context store, selected by ``source=wiki``, so the chat, the
CLI and a later MCP wrapper share one API, one PAT and one quota.

Addresses are ``wiki/<collection>/<slug>[#section]``. The ``authors``
collection is never served, whatever the wiki returns; every answer carries
the ``artifact`` id the wiki reported and a public ``link``.
"""

from __future__ import annotations

import logging
import re
import httpx

from app.config import Settings

from .base import ContextFile, ContextFileNotFound

logger = logging.getLogger(__name__)

WIKI_ADDRESS_PREFIX = "wiki/"
# The collections a reader may see. ``authors`` is excluded on purpose: the
# wiki's author pages are derived attribution, not knowledge to cite.
WIKI_COLLECTIONS = frozenset(
    {"concepts", "topics", "conflicts", "entities", "summaries", "sources",
     "findings", "directions", "data"}
)
EXCLUDED_COLLECTIONS = frozenset({"authors"})
FILE_SOURCE_WIKI = "wiki"


class WikiUnavailableError(RuntimeError):
    """The wiki container could not be asked, or answered with an error.
    Routes report it as 503 ``wiki unavailable``."""


def quartz_anchor(heading: str) -> str:
    """A heading as Quartz anchors it: lower-case, punctuation removed,
    spaces to hyphens (github-slugger's rule, which Quartz uses)."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def parse_wiki_address(address: str) -> tuple[str, str, str | None]:
    """``wiki/<collection>/<slug>[#section]`` → ``(collection, slug, section)``.

    Raises ``ValueError`` for anything else, including the excluded
    ``authors`` collection — an address nobody may read is not an address.
    """
    if not address.startswith(WIKI_ADDRESS_PREFIX):
        raise ValueError(f"Not a wiki address: {address!r}")
    rest, _, section = address[len(WIKI_ADDRESS_PREFIX):].partition("#")
    parts = [p for p in rest.split("/") if p]
    if len(parts) < 2 or any(p in {".", ".."} for p in parts):
        raise ValueError(f"A wiki address is wiki/<collection>/<slug>: {address!r}")
    collection, slug = parts[0], "/".join(parts[1:])
    if collection in EXCLUDED_COLLECTIONS or collection not in WIKI_COLLECTIONS:
        raise ValueError(f"Unknown wiki collection: {collection!r}")
    return collection, slug, (section or None)


def is_excluded(address: str) -> bool:
    """True for anything under an excluded collection (``wiki/authors/...``)."""
    rest = address.removeprefix(WIKI_ADDRESS_PREFIX)
    return rest.split("/", 1)[0] in EXCLUDED_COLLECTIONS


class WikiManager:
    """``find``/``read``/``ls`` against the wiki container's internal API."""

    def __init__(self, settings: Settings, *, client: httpx.AsyncClient | None = None):
        self.url = settings.wiki_internal_url.rstrip("/")
        self.public_url = settings.wiki_public_url.rstrip("/")
        token = settings.wiki_internal_token
        self._token = token.get_secret_value() if token is not None else None
        self._timeout = settings.wiki_internal_timeout_seconds
        self._client = client

    @property
    def configured(self) -> bool:
        return bool(self._token)

    def link(self, address: str, heading: str | None = None) -> str:
        """The public page URL for an address, with the section anchor."""
        collection, slug, section = parse_wiki_address(address)
        url = f"{self.public_url}/{collection}/{slug}"
        anchor = quartz_anchor(heading or section or "")
        return f"{url}#{anchor}" if anchor else url

    async def _get(self, path: str, params: dict) -> dict:
        if not self.configured:
            raise WikiUnavailableError("wiki backend is not configured (BERIL_WIKI_INTERNAL_TOKEN)")
        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            if self._client is not None:
                response = await self._client.get(f"{self.url}{path}", params=params, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(f"{self.url}{path}", params=params, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("Wiki backend unreachable for %s: %s", path, exc)
            raise WikiUnavailableError(f"wiki unreachable: {exc}") from exc
        if response.status_code == 404:
            raise ContextFileNotFound(f"wiki has no {params}")
        if response.status_code >= 400:
            logger.warning("Wiki backend answered %s for %s", response.status_code, path)
            raise WikiUnavailableError(f"wiki answered HTTP {response.status_code}")
        try:
            body = response.json()
        except ValueError as exc:
            raise WikiUnavailableError("wiki answered with a body that is not JSON") from exc
        return body if isinstance(body, dict) else {"results": body}

    async def find(self, query: str, *, scope: str | None = None, limit: int = 10) -> dict:
        """``{artifact, results: [{address, title, heading, text, score, link}]}``.
        ``scope`` is a collection (``concepts``) or ``None`` for everything."""
        params = {"q": query, "k": limit}
        if scope:
            params["scope"] = scope.removeprefix(WIKI_ADDRESS_PREFIX).strip("/")
        body = await self._get("/wiki/_api/search", params)
        results = []
        for hit in body.get("results") or []:
            address = str(hit.get("address") or "")
            if not address or is_excluded(address):
                continue
            try:
                link = self.link(address, hit.get("heading"))
            except ValueError:
                continue
            results.append(
                {
                    "address": address,
                    "title": hit.get("title") or "",
                    "heading": hit.get("heading"),
                    "text": hit.get("text") or "",
                    "score": float(hit.get("score") or 0.0),
                    "link": link,
                }
            )
        return {"artifact": body.get("artifact"), "results": results[:limit]}

    async def read(self, address: str) -> tuple[ContextFile, dict]:
        """A wiki page as a ``ContextFile`` (source ``wiki``), plus
        ``{artifact, title, link, sources}``."""
        collection, slug, section = parse_wiki_address(address)
        body = await self._get("/wiki/_api/read", {"address": address})
        content = body.get("content") or ""
        if not isinstance(content, str):
            raise WikiUnavailableError("wiki read returned no text content")
        file = ContextFile.from_bytes(
            content.encode("utf-8"),
            address=address,
            owner="wiki",
            project=collection,
            path=f"{slug}.md",
            source=FILE_SOURCE_WIKI,
            content_type="text/markdown",
        )
        extra = {
            "artifact": body.get("artifact"),
            "title": body.get("title") or "",
            "link": self.link(address, section),
            "sources": body.get("sources") or [],
        }
        return file, extra

    async def ls(self, path: str | None = None) -> list:
        """Entries under ``wiki/<collection>`` (or the collections at the
        root), excluded collections dropped."""
        rel = (path or "").removeprefix(WIKI_ADDRESS_PREFIX).strip("/")
        if rel and rel.split("/", 1)[0] in EXCLUDED_COLLECTIONS:
            return []
        body = await self._get("/wiki/_api/ls", {"path": rel})
        entries = body.get("entries") if "entries" in body else body.get("results") or []
        kept = []
        for entry in entries:
            address = entry.get("address") if isinstance(entry, dict) else entry
            if not isinstance(address, str) or is_excluded(address):
                continue
            kept.append(entry if isinstance(entry, dict) else {"address": address})
        return kept

    async def source(self, project: str, *, offset: int, length: int) -> bytes:
        """Exact source bytes of ``project``'s report at ``offset``."""
        if not self.configured:
            raise WikiUnavailableError("wiki backend is not configured")
        headers = {"Authorization": f"Bearer {self._token}"}
        params = {"project": project, "offset": offset, "length": length}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self.url}/wiki/_api/source", params=params, headers=headers)
        except httpx.HTTPError as exc:
            raise WikiUnavailableError(f"wiki unreachable: {exc}") from exc
        if response.status_code == 404:
            raise ContextFileNotFound(project)
        if response.status_code >= 400:
            raise WikiUnavailableError(f"wiki answered HTTP {response.status_code}")
        return response.content
