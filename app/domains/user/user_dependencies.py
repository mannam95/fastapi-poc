from typing import Annotated

from fastapi import Depends

from app.core.database import DBSessionDep
from app.core.logging_service import LoggingServiceDep
from app.domains.user.user_service import UserService


def get_user_service(
    session: DBSessionDep,
    logging_service: LoggingServiceDep,
) -> UserService:
    """
    Dependency provider for UserService.

    Creates a new instance of UserService with the provided database session
    and logging service. This function is used by FastAPI's dependency injection
    system to make the service available to route handlers.

    Args:
        session: SQLAlchemy async session for database operations
        logging_service: Service for logging operations

    Returns:
        UserService: An instance of UserService with the session and
        logging service injected
    """
    return UserService(session, logging_service)


# Type annotation for convenience in route function signatures
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
