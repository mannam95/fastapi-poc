from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.process.process_service import ProcessService


def get_process_service(session: DBSessionDep) -> ProcessService:
    """
    Dependency provider for ProcessService

    This function creates a new instance of ProcessService with the provided database session.
    It's used by FastAPI's dependency injection system to inject the service into route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        An instance of ProcessService with the session injected
    """
    return ProcessService(session)


# Type annotation for convenience
ProcessServiceDep = Annotated[ProcessService, Depends(get_process_service)]
