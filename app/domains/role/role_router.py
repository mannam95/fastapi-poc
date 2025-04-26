# app/domains/role/role_router.py
# This file contains the API routes for the role domain

from typing import List
from fastapi import APIRouter, Query, status

from app.domains.role.role_schemas import (
    RoleCreate, 
    RoleUpdate, 
    RoleRead, 
    RoleProcessAssociation
)
from app.domains.role.role_dependencies import RoleServiceDep

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    service: RoleServiceDep,
):
    """Create a new role"""
    role = await service.create_role(role_data)
    return role


@router.get("/", response_model=List[RoleRead])
async def get_roles(
    service: RoleServiceDep,
    offset: int = Query(0, ge=0, description="Skip the first N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of items returned"),
):
    """Get a paginated list of roles"""
    return await service.get_roles(
        offset=offset, 
        limit=limit
    )



@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: int,
    service: RoleServiceDep,
):
    """Get a specific role by ID"""
    return await service.get_role_by_id(role_id)


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_data: RoleUpdate,
    role_id: int,
    service: RoleServiceDep,
):
    """Update a role's information"""
    return await service.update_role(role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    service: RoleServiceDep,
):
    """Delete a role"""
    await service.delete_role(role_id)
    return None


@router.post("/process-association", status_code=status.HTTP_201_CREATED)
async def add_process_to_role(
    association: RoleProcessAssociation,
    service: RoleServiceDep,
):
    """Associate a process with a role"""
    await service.add_process_to_role(association)
    return {"message": "Process added to role successfully"}


@router.delete("/{role_id}/processes/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_process_from_role(
    role_id: int,
    process_id: int,
    service: RoleServiceDep,
):
    """Remove a process association from a role"""
    await service.remove_process_from_role(role_id, process_id)
    return None 