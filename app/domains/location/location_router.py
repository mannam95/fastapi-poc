from typing import List

from fastapi import APIRouter, status

from app.domains.location.location_dependencies import LocationServiceDep
from app.domains.location.location_schemas import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)
from app.domains.shared.exception_response_schemas import ErrorResponse

router = APIRouter()

# CRUD operations


@router.post(
    "/",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Most likely due to foreign key constraint violation",
        },
    },
)
async def create_location(service: LocationServiceDep, location_in: LocationCreate):
    """
    Create a new location.

    Creates a location with specified attributes and optional
    associations to processes.

    Returns the newly created location with all details.

    Raises:
        DatabaseException: If there's a database error
        RelationshipException: If related entities don't exist
    """
    return await service.create_location(location_in)


@router.get("/", response_model=List[LocationResponse])
async def read_locations(
    service: LocationServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    """
    Get a list of locations with pagination.

    Args:
        offset: Number of records to offset
        limit: Maximum number of records to return

    Returns a list of locations with their details and process relationships.

    Raises:
        DatabaseException: If there's a database error
    """
    return await service.get_locations(offset, limit)


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Location not found",
        },
    },
)
async def read_location(
    location_id: int,
    service: LocationServiceDep,
):
    """
    Get a single location by ID.

    Retrieves detailed information about a specific location,
    including its creator and associated processes.

    Raises:
        NotFoundException: If location not found
        DatabaseException: If there's a database error
    """
    return await service.get_location_by_id(location_id)


@router.put(
    "/{location_id}",
    response_model=LocationResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Location not found",
        },
        400: {
            "model": ErrorResponse,
            "description": "Most likely due to foreign key constraint violation",
        },
    },
)
async def update_location(
    location_id: int,
    location_in: LocationUpdate,
    service: LocationServiceDep,
):
    """
    Update an existing location.

    Updates location attributes and/or process relationships.
    Supports partial updates (only specified fields will be updated).

    Returns the updated location with all details.

    Raises:
        NotFoundException: If location not found
        DatabaseException: If there's a database error
        RelationshipException: If there's an issue with relationship operations
    """
    return await service.update_location(location_id, location_in)


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Location not found",
        },
    },
)
async def delete_location(location_id: int, service: LocationServiceDep):
    """
    Delete a location.

    Completely removes a location and its relationships.
    This operation cannot be undone.

    Returns a success message.

    Raises:
        NotFoundException: If location not found
        DatabaseException: If there's a database error
    """
    await service.delete_location(location_id)
    return {"message": "Location deleted successfully"}
