from typing import List
from fastapi import APIRouter, status

from app.domains.location.location_schemas import (
    LocationCreate, 
    LocationRead, 
    LocationUpdate,
    LocationProcessAssociation
)
from app.domains.location.location_dependencies import LocationServiceDep

router = APIRouter()

# CRUD operations

@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    service: LocationServiceDep,
    location_in: LocationCreate
):
    """Create a new location"""
    return await service.create_location(location_in)


@router.get("/", response_model=List[LocationRead])
async def read_locations(
    service: LocationServiceDep,
    offset: int = 0, 
    limit: int = 100,
):
    """Get list of locations"""
    return await service.get_locations(offset, limit)


@router.get("/{location_id}", response_model=LocationRead)
async def read_location(
    location_id: int,
    service: LocationServiceDep,
):
    """Get a single location by ID with all relationships loaded"""
    return await service.get_location_by_id(location_id)


@router.put("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    location_in: LocationUpdate,
    service: LocationServiceDep,
):
    """Update an existing location"""
    return await service.update_location(location_id, location_in)


@router.delete("/{location_id}", response_model=LocationRead)
async def delete_location(
    location_id: int,
    service: LocationServiceDep,
):
    """Delete a location"""
    return await service.delete_location(location_id)

# Process association endpoints

@router.post("/{location_id}/processes", response_model=LocationRead)
async def add_process_to_location(
    location_id: int,
    association_data: LocationProcessAssociation,
    service: LocationServiceDep,
):
    """Add a process to a location"""
    return await service.add_process_to_location(location_id, association_data.process_id)


@router.delete("/{location_id}/processes/{process_id}", response_model=LocationRead)
async def remove_process_from_location(
    location_id: int,
    process_id: int,
    service: LocationServiceDep,
):
    """Remove a process from a location"""
    return await service.remove_process_from_location(location_id, process_id) 