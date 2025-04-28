from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.process.process_service import ProcessService


def get_process_service(session: DBSessionDep) -> ProcessService:
    """
    Dependency provider for ProcessService.

    Creates a new instance of ProcessService with the provided database session.
    This function is used by FastAPI's dependency injection system to
    make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        ProcessService: An instance of ProcessService with the session injected
    """
    return ProcessService(session)


# Type annotation for convenience in route function signatures
ProcessServiceDep = Annotated[ProcessService, Depends(get_process_service)]
