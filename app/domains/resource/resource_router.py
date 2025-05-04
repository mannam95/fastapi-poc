from typing import List

from fastapi import APIRouter, status

from app.domains.resource.resource_dependencies import ResourceServiceDep
from app.domains.resource.resource_schemas import (
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from app.domains.shared.schemas.exception_response_schemas import ErrorResponse

router = APIRouter()

# CRUD operations


@router.post(
    "/",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Most likely due to foreign key constraint violation",
        },
    },
)
async def create_resource(service: ResourceServiceDep, resource_in: ResourceCreate):
    """
    Create a new resource.

    Creates a resource with specified attributes and optional
    associations to processes.

    Returns the newly created resource with all details.

    Raises:
        DatabaseException: If there's a database error
        RelationshipException: If related entities don't exist
    """
    return await service.create_resource(resource_in)


@router.get("/", response_model=List[ResourceResponse])
async def read_resources(
    service: ResourceServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    """
    Get a list of resources with pagination.

    Args:
        offset: Number of records to offset
        limit: Maximum number of records to return

    Returns a list of resources with their details and process relationships.

    Raises:
        DatabaseException: If there's a database error
    """
    return await service.get_resources(offset, limit)


@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Resource not found",
        },
    },
)
async def read_resource(resource_id: int, service: ResourceServiceDep):
    """
    Get a single resource by ID.

    Retrieves detailed information about a specific resource,
    including its creator and associated processes.

    Raises:
        NotFoundException: If resource not found
        DatabaseException: If there's a database error
    """
    return await service.get_resource_by_id(resource_id)


@router.put(
    "/{resource_id}",
    response_model=ResourceResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Resource not found",
        },
        400: {
            "model": ErrorResponse,
            "description": "Most likely due to foreign key constraint violation",
        },
    },
)
async def update_resource(
    resource_id: int, resource_in: ResourceUpdate, service: ResourceServiceDep
):
    """
    Update an existing resource.

    Updates resource attributes and/or process relationships.
    Supports partial updates (only specified fields will be updated).

    Returns the updated resource with all details.

    Raises:
        NotFoundException: If resource not found
        DatabaseException: If there's a database error
        RelationshipException: If there's an issue with relationship operations
    """
    return await service.update_resource(resource_id, resource_in)


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Resource not found",
        },
    },
)
async def delete_resource(resource_id: int, service: ResourceServiceDep):
    """
    Delete a resource.

    Completely removes a resource and its relationships.
    This operation cannot be undone.

    Returns None

    Raises:
        NotFoundException: If resource not found
        DatabaseException: If there's a database error
    """
    return await service.delete_resource(resource_id)
