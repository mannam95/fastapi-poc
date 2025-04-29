from typing import Any, Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception class for application-specific exceptions"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "An unexpected error occurred"

    def __init__(self, detail: str = "None", headers: Optional[dict[str, Any]] = None):
        """Initialize with status code from the class and optional detail message"""
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=headers,
        )


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found"""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class DatabaseException(AppException):
    """Exception raised when a database operation fails"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Database operation failed"


class ValidationException(AppException):
    """Exception raised when data validation fails"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Data validation failed"


class RelationshipException(AppException):
    """Exception raised when there's an issue with relationship operations"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid relationship operation"


class UnauthorizedException(AppException):
    """Exception raised when a user is not authorized to perform an action"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authorized to perform this action"


class UnexpectedException(AppException):
    """Exception raised when an unexpected error occurs"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "An unexpected error occurred"
