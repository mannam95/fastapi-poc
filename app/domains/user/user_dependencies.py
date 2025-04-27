from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.user.user_service import UserService


def get_user_service(session: DBSessionDep) -> UserService:
    """
    Dependency provider for UserService

    This function creates a new instance of UserService with the provided database session.
    It's used by FastAPI's dependency injection system to inject the service into route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        An instance of UserService with the session injected
    """
    return UserService(session)


# Type annotation for convenience
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
