import functools
import inspect
import socket
from typing import Any, Callable, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.exceptions import (
    DatabaseException,
    NotFoundException,
    RelationshipException,
    UnexpectedException,
)
from app.utils.logging_service import BaseLoggingService

# Create a type variable for return values
T = TypeVar("T")


class ServiceMetaclass(type):
    """
    Metaclass that automatically wraps async service methods with exception handling.

    This metaclass examines all methods in a class during definition and
    wraps any async method with our exception handling logic, so service
    classes don't need to manually handle exceptions or use inner functions.
    """

    def __new__(mcs, name, bases, attrs):
        for attr_name, attr_value in list(attrs.items()):
            # Only process async methods that aren't private/dunder methods
            if (
                attr_name.startswith("__") or not attr_name.startswith("_")
            ) and inspect.iscoroutinefunction(attr_value):
                attrs[attr_name] = ServiceMetaclass._wrap_with_exception_handling(attr_value)

        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def _wrap_with_exception_handling(method: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap an async method with standard exception handling."""

        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            exception_to_raise = None
            try:
                return await method(self, *args, **kwargs)
            except NotFoundException as e:
                # Pass through our custom not found exceptions
                exception_to_raise = e
            except RelationshipException as e:
                # Pass through our custom relationship exceptions
                exception_to_raise = e
            except IntegrityError as e:
                # Handle constraint violations
                exception_to_raise = RelationshipException(
                    f"Integrity error most likely due to foreign key constraint violation: {str(e)}"
                )
            except SQLAlchemyError as e:
                # Handle all other database errors that occur at the SQLAlchemy level
                exception_to_raise = DatabaseException(f"SQLAlchemyError database error: {str(e)}")
            except (socket.gaierror, ConnectionRefusedError) as e:
                # Handle network-related errors or if db is unreachable
                exception_to_raise = DatabaseException(f"Database not reachable: {str(e)}")
            except Exception as e:
                # Handle all other unexpected errors
                exception_to_raise = UnexpectedException(f"Unexpected error: {str(e)}")
            finally:
                # Only rollback if there was an exception and we have a session
                if exception_to_raise and hasattr(self, "session"):
                    await self.session.rollback()

            # Re-raise the exception outside the try-finally block
            if exception_to_raise:
                await self.logging_service.log_business_exception(exception_to_raise)
                raise exception_to_raise

        return wrapper


class ExceptionHandlingServiceBase(metaclass=ServiceMetaclass):
    """
    Base service class with automatic exception handling for all methods.

    This class uses the ServiceMetaclass to automatically wrap all async methods
    with exception handling, eliminating the need for repetitive try-except blocks
    in service methods.

    All service classes should inherit from this class.
    """

    def __init__(self, session: AsyncSession, logging_service: BaseLoggingService):
        """Initialize with database session.

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Logging service for logging exceptions
        """
        self.session = session
        self.logging_service = logging_service
