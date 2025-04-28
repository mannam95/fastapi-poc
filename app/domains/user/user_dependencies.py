from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.domains.user.user_service import UserService


def get_user_service(session: DBSessionDep) -> UserService:
    """
    Dependency provider for UserService.

    Creates a new instance of UserService with the provided database session.
    This function is used by FastAPI's dependency injection system to
    make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations

    Returns:
        UserService: An instance of UserService with the session injected
    """
    return UserService(session)


# Type annotation for convenience in route function signatures
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
