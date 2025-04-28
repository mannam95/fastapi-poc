from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.resource.resource_service import ResourceService


def get_resource_service(session: DBSessionDep) -> ResourceService:
    """
    Dependency provider for ResourceService.

    Creates a new instance of ResourceService with the provided database session.
    This function is used by FastAPI's dependency injection system to
    make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        ResourceService: An instance of ResourceService with the session injected
    """
    return ResourceService(session)


# Type annotation for convenience in route function signatures
ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
