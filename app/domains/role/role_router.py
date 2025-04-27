# app/domains/role/role_router.py
# This file contains the API routes for the role domain

from typing import List

from fastapi import APIRouter, Query, status

from app.domains.role.role_dependencies import RoleServiceDep
from app.domains.role.role_schemas import RoleCreate, RoleRead, RoleUpdate

router = APIRouter()


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    service: RoleServiceDep,
):
    """Create a new role"""
    return await service.create_role(role_data)


@router.get("/", response_model=List[RoleRead])
async def get_roles(
    service: RoleServiceDep,
    offset: int = Query(0, ge=0, description="Skip the first N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of items returned"),
):
    """Get a paginated list of roles"""
    return await service.get_roles(offset=offset, limit=limit)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: int,
    service: RoleServiceDep,
):
    """Get a specific role by ID"""
    return await service.get_role_by_id(role_id)


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    service: RoleServiceDep,
):
    """Update a role's information"""
    return await service.update_role(role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: int,
    service: RoleServiceDep,
):
    """Delete a role"""
    await service.delete_role(role_id)
    return {"message": "Role deleted successfully"}
