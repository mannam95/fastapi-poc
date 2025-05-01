import datetime
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
            pool_size=50,
            # If all 50 in the pool_size connections are busy,
            # Then SQLAlchemy can open up to 50 more (totaling 100)
            # But these "overflow" connections are not reused and are closed when returned
            # In total, this means that the pool can have up to pool_size + max_overflow connections
            max_overflow=50,
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
            await conn.run_sync(Base.metadata.create_all)


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


async def create_db_and_tables():
    """
    Initialize the database and create all tables.
    Should be called during application startup.
    """
    try:
        await sessionmanager.create_all()
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        raise


# use the DBSessionDep via dependency injection
async def create_initial_data():
    """
    Create initial data for the database.
    Creates sample users, departments, locations, resources, roles, and processes.
    """
    try:
        from app.domains.department.department_model import Department
        from app.domains.location.location_model import Location
        from app.domains.process.process_model import Process
        from app.domains.resource.resource_model import Resource
        from app.domains.role.role_model import Role
        from app.domains.user.user_model import User

        # get session
        session = sessionmanager.session()

        # create two users
        user1 = User(title="user1", created_at=datetime.datetime.now())
        user2 = User(title="user2", created_at=datetime.datetime.now())

        # Add and flush users first to get their IDs
        session.add_all([user1, user2])
        await session.flush()

        # create two departments
        department1 = Department(
            title="department1",
            created_at=datetime.datetime.now(),
            created_by_id=user1.id,
        )
        department2 = Department(
            title="department2",
            created_at=datetime.datetime.now(),
            created_by_id=user2.id,
        )

        # create two locations
        location1 = Location(
            title="location1",
            created_at=datetime.datetime.now(),
            created_by_id=user1.id,
        )
        location2 = Location(
            title="location2",
            created_at=datetime.datetime.now(),
            created_by_id=user2.id,
        )

        # create two resources
        resource1 = Resource(
            title="resource1",
            created_at=datetime.datetime.now(),
            created_by_id=user1.id,
        )
        resource2 = Resource(
            title="resource2",
            created_at=datetime.datetime.now(),
            created_by_id=user2.id,
        )

        # create two roles
        role1 = Role(title="role1", created_at=datetime.datetime.now(), created_by_id=user1.id)
        role2 = Role(title="role2", created_at=datetime.datetime.now(), created_by_id=user2.id)

        # create two processes
        process1 = Process(
            title="process1",
            created_at=datetime.datetime.now(),
            created_by_id=user1.id,
            departments=[department1],
            locations=[location1],
            resources=[resource1],
            roles=[role1],
        )
        process2 = Process(
            title="process2",
            created_at=datetime.datetime.now(),
            created_by_id=user2.id,
            departments=[department2],
            locations=[location2],
            resources=[resource2],
            roles=[role2],
        )

        # Add all remaining objects
        session.add_all(
            [
                department1,
                department2,
                location1,
                location2,
                resource1,
                resource2,
                role1,
                role2,
                process1,
                process2,
            ]
        )

        await session.commit()
        await session.close()
    except Exception as e:
        print(f"Error creating initial data: {str(e)}")
        raise
