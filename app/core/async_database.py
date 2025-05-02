from asyncio import TaskGroup, current_task
from typing import Annotated, AsyncGenerator, Iterable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.core.database import sessionmanager


def _get_current_task_id() -> int:
    return id(current_task())


class AsyncDatabaseSessionManager:
    """
    Manages database connections and session creation.
    Provides an abstraction for creating and managing SQLAlchemy async sessions.
    """

    def __init__(self):
        if sessionmanager._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized. Call init() first.")

        self.scoped_session_factory = async_scoped_session(
            sessionmanager._sessionmaker, scopefunc=_get_current_task_id
        )

    def get_session(self) -> AsyncSession:
        return self.scoped_session_factory()


async def get_db_manager() -> AsyncGenerator[AsyncDatabaseSessionManager, None]:
    db_manager = AsyncDatabaseSessionManager()
    try:
        yield db_manager
    finally:
        sessions = db_manager.scoped_session_factory.registry.registry.values()
        await _close_sessions(sessions)


async def _close_sessions(db_sessions: Iterable[AsyncSession]):
    async with TaskGroup() as task_group:
        for db_session in db_sessions:
            task_group.create_task(db_session.close())


# Type annotation for the database session dependency
AsyncDBSessionManagerDep = Annotated[AsyncDatabaseSessionManager, Depends(get_db_manager)]
