from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class FileMetadata(BaseModel):
    created: datetime
    owner: str
    last_changed: datetime
    path: Path

class ContextFile(BaseModel):
    """
    A class representing a file stored in the context manager.
    """
    content: str
    metadata: FileMetadata

class ContextQuery(BaseModel):
    query: str
    root_path: str | None = None
    limit: int = 10
    score_threshold: float | None = None

class QueryResult(BaseModel):
    uri: str
    context_type: str
    score: float
    text: str

class ContextQueryResults(BaseModel):
    query: str
    results: list[QueryResult]

class ContextManager:
    url: str
    config: dict[str, str]

    async def get_file(self, path: Path) -> ContextFile:
        ...

    async def insert_file(self, file: ContextFile) -> bool:
        ...

    async def list_files(self) -> list[ContextFile]:
        ...

    async def query(self, query: ContextQuery) -> ContextQueryResults:
        ...

