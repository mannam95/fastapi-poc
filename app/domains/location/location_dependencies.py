from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.location.location_service import LocationService


def get_location_service(session: DBSessionDep) -> LocationService:
    """
    Dependency provider for LocationService

    This function creates a new instance of LocationService with the provided database session.
    It's used by FastAPI's dependency injection system to inject the service into route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        An instance of LocationService with the session injected
    """
    return LocationService(session)


# Type annotation for convenience
LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
