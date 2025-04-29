import asyncio
from typing import AsyncGenerator, Generator
from urllib.parse import urlparse

import psycopg2
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, get_db_session, sessionmanager
from app.core.logging_service import get_logging_service
from tests.mocks.mock_logging_service import MockLoggingService

TEST_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI


# Initialize FastAPI app for testing
@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI test app with routes"""
    app = FastAPI()
    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


# Initialize test database
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for pytest-asyncio"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def init_test_db() -> AsyncGenerator[None, None]:
    """Initialize the test database"""
    # Create test database engine
    engine = create_async_engine(TEST_DATABASE_URL)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Parse the connection string to get components for psycopg2
    parsed_url = urlparse(TEST_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))
    db_params = {
        "dbname": parsed_url.path[1:],
        "user": parsed_url.username,
        "password": parsed_url.password,
        "host": parsed_url.hostname,
        "port": parsed_url.port or 5432,
    }

    # Use psycopg2 to execute the SQL script directly
    with psycopg2.connect(**db_params) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            with open("sql-scripts/init.sql", "r") as f:
                cursor.execute(f.read())

    # Initialize session manager with test database
    sessionmanager.init(TEST_DATABASE_URL)

    yield

    # Clean up
    if sessionmanager._engine is not None:
        await sessionmanager.close()
    await engine.dispose()


@pytest.fixture
async def db_session(init_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    async with sessionmanager.session() as session:
        # Start transaction
        transaction = await session.begin()

        yield session

        # Rollback transaction after test - handle case where it might be closed
        try:
            if transaction.is_active:
                await transaction.rollback()
        except Exception as e:
            print(f"Error during transaction rollback: {e}")
        finally:
            await session.close()


@pytest.fixture
async def client(app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with a clean database session"""

    # Override the dependency to use our test database session
    async def override_get_db_session():
        yield db_session

    # Override the logging service with our mock
    def override_get_logging_service():
        return MockLoggingService()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_logging_service] = override_get_logging_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
