from typing import List

from fastapi import APIRouter, status

from app.domains.shared.exception_response_schemas import ErrorResponse
from app.domains.user.user_dependencies import UserServiceDep
from app.domains.user.user_schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Most likely due to foreign key constraint violation",
        },
    },
)
async def create_user(
    user_in: UserCreate,
    service: UserServiceDep,
):
    """
    Creates a user with the specified title.
    Users serve as creators for other entities in the system.

    Returns the newly created user with all details.

    Raises:
        DatabaseException: If there's a database error
    """
    return await service.create_user(user_in)


@router.get("/", response_model=List[UserResponse])
async def read_users(
    service: UserServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    """
    Get a list of users with pagination.

    Args:
        offset: Number of records to offset
        limit: Maximum number of records to return

    Returns a list of users with their details.

    Raises:
        DatabaseException: If there's a database error
    """
    return await service.get_users(offset, limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "User not found",
        },
    },
)
async def read_user(
    user_id: int,
    service: UserServiceDep,
):
    """
    Get a single user by ID.

    Retrieves detailed information about a specific user.

    Raises:
        NotFoundException: If user not found
        DatabaseException: If there's a database error
    """
    return await service.get_user_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "User not found",
        },
        400: {
            "model": ErrorResponse,
            "description": "Most likely due to foreign key constraint violation",
        },
    },
)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: UserServiceDep,
):
    """
    Update an existing user.

    Updates user attributes.
    Supports partial updates (only specified fields will be updated).

    Returns the updated user with all details.

    Raises:
        NotFoundException: If user not found
        DatabaseException: If there's a database error
    """
    return await service.update_user(user_id, user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "User not found",
        },
    },
)
async def delete_user(user_id: int, service: UserServiceDep):
    """
    Delete a user.

    Completely removes a user from the system.
    This operation cannot be undone.

    Returns a success message.

    Raises:
        NotFoundException: If user not found
        DatabaseException: If there's a database error
    """
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}
