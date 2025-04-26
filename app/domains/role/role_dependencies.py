from fastapi import Depends
from typing import Annotated

from app.core.database import DBSessionDep
from app.domains.role.role_service import RoleService

def get_role_service(session: DBSessionDep) -> RoleService:
    """
    Dependency provider for RoleService
    
    This function creates a new instance of RoleService with the provided database session.
    It's used by FastAPI's dependency injection system to inject the service into route handlers.
    
    Args:
        session: SQLAlchemy async session for database operations
        
    Returns:
        An instance of RoleService with the session injected
    """
    return RoleService(session)

# Type annotation for convenience
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)] 