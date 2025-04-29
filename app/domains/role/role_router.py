# app/domains/role/role_router.py
# This file contains the API routes for the role domain

from typing import List

from fastapi import APIRouter, Query, status

from app.domains.role.role_dependencies import RoleServiceDep
from app.domains.role.role_schemas import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    service: RoleServiceDep,
):
    """
    Create a new role.

    Creates a role with specified attributes and optional
    associations to processes.

    Returns the newly created role with all details.

    Raises:
        DatabaseException: If there's a database error
        RelationshipException: If related entities don't exist
    """
    return await service.create_role(role_data)


@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    service: RoleServiceDep,
    offset: int = Query(0, ge=0, description="Skip the first N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of items returned"),
):
    """
    Get a list of roles with pagination.

    Args:
        offset: Number of records to offset
        limit: Maximum number of records to return

    Returns a list of roles with their details and process relationships.

    Raises:
        DatabaseException: If there's a database error
    """
    return await service.get_roles(offset=offset, limit=limit)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    service: RoleServiceDep,
):
    """
    Get a single role by ID.

    Retrieves detailed information about a specific role,
    including its creator and associated processes.

    Raises:
        NotFoundException: If role not found
        DatabaseException: If there's a database error
    """
    return await service.get_role_by_id(role_id)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    service: RoleServiceDep,
):
    """
    Update an existing role.

    Updates role attributes and/or process relationships.
    Supports partial updates (only specified fields will be updated).

    Returns the updated role with all details.

    Raises:
        NotFoundException: If role not found
        DatabaseException: If there's a database error
        RelationshipException: If there's an issue with relationship operations
    """
    return await service.update_role(role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: int,
    service: RoleServiceDep,
):
    """
    Delete a role.

    Completely removes a role and its relationships.
    This operation cannot be undone.

    Returns a success message.

    Raises:
        NotFoundException: If role not found
        DatabaseException: If there's a database error
    """
    await service.delete_role(role_id)
    return {"message": "Role deleted successfully"}
