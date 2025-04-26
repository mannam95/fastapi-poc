from fastapi import Depends
from typing import Annotated

from app.core.database import DBSessionDep
from app.domains.department.department_service import DepartmentService

def get_department_service(session: DBSessionDep) -> DepartmentService:
    """
    Dependency provider for DepartmentService
    
    This function creates a new instance of DepartmentService with the provided database session.
    It's used by FastAPI's dependency injection system to inject the service into route handlers.
    
    Args:
        session: SQLAlchemy async session for database operations
        
    Returns:
        An instance of DepartmentService with the session injected
    """
    return DepartmentService(session)

# Type annotation for convenience
DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)] 