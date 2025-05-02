from typing import Annotated

from fastapi import Depends

from app.core.async_database import AsyncDBSessionManagerDep
from app.core.database import DBSessionDep
from app.core.logging_service import LoggingServiceDep
from app.domains.role.role_service import RoleService


def get_role_service(
    session: DBSessionDep,
    async_db_session_manager: AsyncDBSessionManagerDep,
    logging_service: LoggingServiceDep,
) -> RoleService:
    """
    Dependency provider for RoleService.

    Creates a new instance of RoleService with the provided database session
    and logging service. This function is used by FastAPI's dependency injection
    system to make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations
        logging_service: Service for logging operations

    Returns:
        RoleService: An instance of RoleService with dependencies injected
    """
    return RoleService(session, async_db_session_manager, logging_service)


# Type annotation for convenience in route function signatures
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
