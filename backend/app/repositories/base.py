import uuid
from types import TracebackType
from typing import Protocol, Self

from app.models.brief import Brief
from app.schemas.api import BriefUpdate


class BriefRepository(Protocol):
    """Protocol for Brief database operations with context management."""

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    async def create(self, text: str) -> Brief:
        """Creates a new Brief record."""
        ...

    async def get(self, brief_id: uuid.UUID) -> Brief | None:
        """Retrieves a Brief record by ID."""
        ...

    async def update(self, brief_id: uuid.UUID, update_data: BriefUpdate) -> Brief:
        """Updates fields of a Brief record using structured Pydantic data."""
        ...
