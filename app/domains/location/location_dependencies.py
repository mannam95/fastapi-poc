from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.location.location_service import LocationService


def get_location_service(session: DBSessionDep) -> LocationService:
    """
    Dependency provider for LocationService.

    Creates a new instance of LocationService with the provided database session.
    This function is used by FastAPI's dependency injection system to
    make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        LocationService: An instance of LocationService with the session injected
    """
    return LocationService(session)


# Type annotation for convenience in route function signatures
LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
