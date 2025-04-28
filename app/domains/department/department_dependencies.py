from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.department.department_service import DepartmentService


def get_department_service(session: DBSessionDep) -> DepartmentService:
    """
    Dependency provider for DepartmentService.

    Creates a new instance of DepartmentService with the provided database session.
    This function is used by FastAPI's dependency injection system to
    make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        DepartmentService: An instance of DepartmentService with the session injected
    """
    return DepartmentService(session)


# Type annotation for convenience in route function signatures
DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)]
