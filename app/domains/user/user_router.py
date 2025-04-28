from typing import List

from fastapi import APIRouter, status

from app.domains.user.user_dependencies import UserServiceDep
from app.domains.user.user_schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(service: UserServiceDep, user_in: UserCreate):
    """
    Create a new user.

    Creates a user with the specified title.
    Users serve as creators for other entities in the system.

    Returns the newly created user with all details.
    """
    return await service.create_user(user_in)


@router.get("/", response_model=List[UserRead])
async def read_users(
    service: UserServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get a list of users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns a list of users with their details.
    """
    return await service.get_users(skip, limit)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    service: UserServiceDep,
):
    """
    Get a single user by ID.

    Retrieves detailed information about a specific user.

    Raises 404 if user not found.
    """
    return await service.get_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserRead)
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
    Raises 404 if user not found.
    """
    return await service.update_user(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    service: UserServiceDep,
):
    """
    Delete a user.

    Completely removes a user from the system.
    This operation cannot be undone.

    Returns a success message.
    Raises 404 if user not found.
    """
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}
