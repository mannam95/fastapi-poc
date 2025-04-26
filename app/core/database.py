from typing import Annotated, AsyncIterator, Union

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine.url import URL


Base = declarative_base()
SCHEMA = "public"  # Default PostgreSQL schema

class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: Union[str, URL]):
        """Initialize the database engine with the given URL
        
        Args:
            host: Database URL as string or SQLAlchemy URL object
        """
        # Ensure we have a string for the database URL
        host_str = str(host) if not isinstance(host, str) else host
        
        self._engine = create_async_engine(
            url=host_str, 
            pool_size=10, 
            max_overflow=0, 
            pool_pre_ping=True
        )
        self._sessionmaker = async_sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None
        
    def session(self) -> AsyncSession:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        return self._sessionmaker()
        
    async def create_all(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        
        # Create tables
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

sessionmanager = DatabaseSessionManager()

async def get_db_session() -> AsyncIterator[AsyncSession]:
    session = sessionmanager.session()
    try:
        # Set search path only if a specific schema is defined
        if SCHEMA != "public":
            await session.execute(
                text(f"SET search_path TO {SCHEMA}")
            )
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        # Closing the session after use...
        await session.close()


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]

async def create_db_and_tables():
    """Initialize the database and create all tables"""
    try:       
        await sessionmanager.create_all()
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        raise