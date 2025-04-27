from typing import List
from fastapi import APIRouter, status

from app.domains.user.user_schemas import UserCreate, UserRead, UserUpdate
from app.domains.user.user_dependencies import UserServiceDep

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    service: UserServiceDep,
    user_in: UserCreate
):
    """Create a new user"""
    return await service.create_user(user_in)


@router.get("/", response_model=List[UserRead])
async def read_users(
    service: UserServiceDep,
    skip: int = 0, 
    limit: int = 100,
):
    """Get list of users"""
    return await service.get_users(skip, limit)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    service: UserServiceDep,
):
    """Get a single user by ID"""
    return await service.get_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: UserServiceDep,
):
    """Update an existing user"""
    return await service.update_user(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    service: UserServiceDep,
):
    """Delete a user"""
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}
