from app.db.session import async_session
from app.repositories.base import BriefRepository
from app.repositories.brief import SQLAlchemyBriefRepository


def get_brief_repository() -> BriefRepository:
    """Dependency provider helper for retrieving the repository."""
    return SQLAlchemyBriefRepository(async_session)


__all__ = [
    "BriefRepository",
    "SQLAlchemyBriefRepository",
    "get_brief_repository",
]
