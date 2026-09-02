from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from app.db.models import BerilUser

class GlobalPerm(Enum):
    NONE: 1
    READ: 2

@dataclass
class FileMetadata:
    created: datetime
    owner: BerilUser
    last_changed: datetime
    global_permissions: GlobalPerm
    path: Path

@dataclass
class ContextFile:
    """
    A class representing a file stored in the context manager.
    """
    content: str
    metadata: FileMetadata

@dataclass
class QueryResult:
    uri: str
    context_type: str
    score: float
    text: str

@dataclass
class ContextQueryResults:
    query: str
    status: str
    results: list[QueryResult]

class ContextManager:
    url: str
    config: dict[str, str]

    async def get_file(self, user: BerilUser, path: Path) -> ContextFile:
        ...

    async def insert_file(self, user: BerilUser, file: ContextFile) -> bool:
        ...

    async def list_files(self, user: BerilUser) -> list[ContextFile]:
        ...

    async def query(self, user: BerilUser, query: str) -> ContextQueryResults:
        ...

