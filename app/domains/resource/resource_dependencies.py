from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.core.logging_service import LoggingServiceDep
from app.domains.resource.resource_service import ResourceService


def get_resource_service(
    session: DBSessionDep,
    logging_service: LoggingServiceDep,
) -> ResourceService:
    """
    Dependency provider for ResourceService.

    Creates a new instance of ResourceService with the provided database session
    and logging service. This function is used by FastAPI's dependency injection
    system to make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations
        logging_service: Service for logging operations

    Returns:
        ResourceService: An instance of ResourceService with the session and
        logging service injected
    """
    return ResourceService(session, logging_service)


# Type annotation for convenience in route function signatures
ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
