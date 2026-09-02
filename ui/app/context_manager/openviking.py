from pathlib import Path

from app.clients.openviking import OpenVikingClient
from app.config import Settings

from .base import ContextFile, ContextManager, ContextQueryResults


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
        ov_client.close()
        return results

    async def query(self, query: str) -> ContextQueryResults:
        ov_client = await OpenVikingClient.create(self.api_key, base_url=self.url)
        results = await ov_client.search(query)
        ov_client.close()
        return results
