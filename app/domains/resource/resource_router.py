from typing import List

from fastapi import APIRouter, status

from app.domains.resource.resource_dependencies import ResourceServiceDep
from app.domains.resource.resource_schemas import (
    ResourceCreate,
    ResourceRead,
    ResourceUpdate,
)

router = APIRouter()

# CRUD operations


@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
async def create_resource(service: ResourceServiceDep, resource_in: ResourceCreate):
    """Create a new resource"""
    return await service.create_resource(resource_in)


@router.get("/", response_model=List[ResourceRead])
async def read_resources(
    service: ResourceServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    """Get list of resources"""
    return await service.get_resources(offset, limit)


@router.get("/{resource_id}", response_model=ResourceRead)
async def read_resource(
    resource_id: int,
    service: ResourceServiceDep,
):
    """Get a single resource by ID with all relationships loaded"""
    return await service.get_resource_by_id(resource_id)


@router.put("/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: int,
    resource_in: ResourceUpdate,
    service: ResourceServiceDep,
):
    """Update an existing resource"""
    return await service.update_resource(resource_id, resource_in)


@router.delete("/{resource_id}", status_code=status.HTTP_200_OK)
async def delete_resource(
    resource_id: int,
    service: ResourceServiceDep,
):
    """Delete a resource"""
    await service.delete_resource(resource_id)
    return {"message": "Resource deleted successfully"}
