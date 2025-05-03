from typing import Annotated, AsyncIterator, Union

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

SCHEMA = "public"  # Default PostgreSQL schema


class Base(DeclarativeBase):
    pass


class DatabaseSessionManager:
    """
    Manages database connections and session creation.
    Provides an abstraction for creating and managing SQLAlchemy async sessions.
    """

    def __init__(self):
        """Initialize DatabaseSessionManager with no engine or sessionmaker"""
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: Union[str, URL]):
        """
        Initialize the database engine with the given URL.

        Args:
            host: Database URL as string or SQLAlchemy URL object
        """
        # Ensure we have a string for the database URL
        host_str = str(host) if not isinstance(host, str) else host

        self._engine = create_async_engine(
            url=host_str,
            # This determines how many requests can use a DB connection at the same time
            # before waiting. But pool_size connections are reused and are not closed
            # when returned. They are only closed when the engine is disposed.
            pool_size=10,
            # If all 50 in the pool_size connections are busy,
            # Then SQLAlchemy can open up to 50 more (totaling 100)
            # But these "overflow" connections are not reused and are closed when returned
            # In total, this means that the pool can have up to pool_size + max_overflow connections
            max_overflow=5,
            # This is the maximum time (in seconds) a request will wait for a connection.
            # If the pool is full (i.e., all connections are in use and max overflow is reached).
            # If no connection is available within this time, it raises a TimeoutError
            pool_timeout=30,
            # Before handing a connection to the app, SQLAlchemy will issue a
            # lightweight "ping" (SELECT 1) to make sure the connection is alive.
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    async def close(self):
        """
        Close the database engine and clean up resources.
        Raises exception if called before initialization.
        """
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    def session(self) -> AsyncSession:
        """
        Create and return a new database session.

        Returns:
            AsyncSession: A new SQLAlchemy async session

        Raises:
            Exception: If manager is not initialized
        """
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        return self._sessionmaker()

    async def create_all(self):
        """
        Create all database tables defined in SQLAlchemy models.

        Raises:
            Exception: If manager is not initialized
        """
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        # Create tables
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)


sessionmanager = DatabaseSessionManager()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency that provides a database session and handles cleanup.
    Yields an active session and ensures proper cleanup after use.

    Yields:
        AsyncSession: SQLAlchemy async session for database operations
    """
    session = sessionmanager.session()
    try:
        # Set search path only if a specific schema is defined
        if SCHEMA != "public":
            await session.execute(text(f"SET search_path TO {SCHEMA}"))
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        # Closing the session after use...
        await session.close()


# Type annotation for the database session dependency
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
