from pathlib import Path

from app.clients.openviking import OpenVikingClient
from app.config import Settings

from .base import (
    ContextFile,
    ContextManager,
    ContextQuery,
    ContextQueryResults,
    QueryResult,
)


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
