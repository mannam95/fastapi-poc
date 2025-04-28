from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.role.role_service import RoleService


def get_role_service(session: DBSessionDep) -> RoleService:
    """
    Dependency provider for RoleService.

    Creates a new instance of RoleService with the provided database session.
    This function is used by FastAPI's dependency injection system to
    make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        RoleService: An instance of RoleService with the session injected
    """
    return RoleService(session)


# Type annotation for convenience in route function signatures
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
