from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.core.logging_service import LoggingServiceDep
from app.domains.process.process_service import ProcessService


def get_process_service(
    session: DBSessionDep,
    logging_service: LoggingServiceDep,
) -> ProcessService:
    """
    Dependency provider for ProcessService.

    Creates a new instance of ProcessService with the provided database session
    and logging service. This function is used by FastAPI's dependency injection
    system to make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations
        logging_service: Service for logging operations

    Returns:
        ProcessService: An instance of ProcessService with the session and
        logging service injected
    """
    return ProcessService(session, logging_service)


# Type annotation for convenience in route function signatures
ProcessServiceDep = Annotated[ProcessService, Depends(get_process_service)]
