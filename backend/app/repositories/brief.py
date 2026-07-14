import uuid
from types import TracebackType
from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.exceptions import BriefNotFoundError, RepositoryContextError
from app.models.brief import Brief
from app.repositories.base import BriefRepository
from app.schemas.api import BriefUpdate


class SQLAlchemyBriefRepository(BriefRepository):
    """SQLAlchemy-backed implementation of BriefRepository context manager."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.session:
            try:
                if exc_type is None:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()
                self.session = None

    async def create(self, text: str) -> Brief:
        if not self.session:
            raise RepositoryContextError()
        db_brief = Brief(input_text=text, status="pending")
        self.session.add(db_brief)
        await self.session.flush()
        return db_brief

    async def get(self, brief_id: uuid.UUID) -> Brief | None:
        if not self.session:
            raise RepositoryContextError()
        stmt = select(Brief).where(Brief.id == brief_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, brief_id: uuid.UUID, update_data: BriefUpdate) -> Brief:
        if not self.session:
            raise RepositoryContextError()
        db_brief = await self.get(brief_id)
        if not db_brief:
            raise BriefNotFoundError(brief_id)

        # Update fields from Pydantic model dump
        dump = update_data.model_dump(exclude_unset=True)
        for key, value in dump.items():
            if hasattr(db_brief, key):
                setattr(db_brief, key, value)

        await self.session.flush()
        return db_brief
