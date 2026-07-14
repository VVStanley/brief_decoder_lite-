# ruff: noqa: E402
import os

# Force testing environment for Dynaconf BEFORE importing any application code
os.environ["ENV_FOR_DYNACONF"] = "testing"

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """Automatically creates the test database and all tables once per test session."""
    # 1. Connect to the default 'postgres' database to ensure the test database exists
    # Use isolation_level="AUTOCOMMIT" so we can execute CREATE DATABASE
    admin_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname='brief_decoder_test'")
        )
        if not result.scalar():
            await conn.execute(text("CREATE DATABASE brief_decoder_test"))
    await admin_engine.dispose()

    # 2. Connect to the newly created/existing test database and create tables
    engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Clean up: drop all tables in the test database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Creates an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Creates a fresh, isolated database session bound to the active test event loop."""
    engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
        await session.commit()
    await engine.dispose()


from fastapi import FastAPI


@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    """Fixture that returns a configured FastAPI app with db override."""
    app = create_app()

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async client fixture for testing endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
