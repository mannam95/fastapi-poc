from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.resource.resource_service import ResourceService


def get_resource_service(session: DBSessionDep) -> ResourceService:
    """
    Dependency provider for ResourceService

    This function creates a new instance of ResourceService with the provided database session.
    It's used by FastAPI's dependency injection system to inject the service into route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        An instance of ResourceService with the session injected
    """
    return ResourceService(session)


# Type annotation for convenience
ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
