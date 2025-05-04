from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.department.department_service import DepartmentService
from app.utils.logging_service import LoggingServiceDep


def get_department_service(
    session: DBSessionDep,
    logging_service: LoggingServiceDep,
) -> DepartmentService:
    """
    Dependency provider for DepartmentService.

    Creates a new instance of DepartmentService with the provided database session
    and logging service. This function is used by FastAPI's dependency injection
    system to make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations
        logging_service: Service for logging operations

    Returns:
        DepartmentService: An instance of DepartmentService with the session and
        logging service injected
    """
    return DepartmentService(session, logging_service)


# Type annotation for convenience in route function signatures
DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)]
