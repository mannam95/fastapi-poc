from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.core.logging_service import LoggingServiceDep
from app.domains.location.location_service import LocationService


def get_location_service(
    session: DBSessionDep,
    logging_service: LoggingServiceDep,
) -> LocationService:
    """
    Dependency provider for LocationService.

    Creates a new instance of LocationService with the provided database session
    and logging service. This function is used by FastAPI's dependency injection
    system to make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations
        logging_service: Service for logging operations

    Returns:
        LocationService: An instance of LocationService with the session and
        logging service injected
    """
    return LocationService(session, logging_service)


# Type annotation for convenience in route function signatures
LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
