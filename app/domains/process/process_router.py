from typing import List

from fastapi import APIRouter, status

from app.domains.process.process_dependencies import ProcessServiceDep
from app.domains.process.process_schemas import (
    ProcessCreate,
    ProcessResponse,
    ProcessUpdate,
)

router = APIRouter()


@router.post("/", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_process(service: ProcessServiceDep, process_in: ProcessCreate):
    """
    Create a new process.

    Creates a process with specified attributes and relationships to
    departments, locations, resources, and roles.

    Returns the newly created process with all details.
    """
    return await service.create_process(process_in)


@router.get("/", response_model=List[ProcessResponse])
async def read_processes(
    service: ProcessServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get a list of processes with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns a list of processes with all their details and relationships.
    """
    return await service.get_processes(skip, limit)


@router.get("/{process_id}", response_model=ProcessResponse)
async def read_process(
    process_id: int,
    service: ProcessServiceDep,
):
    """
    Get a single process by ID.

    Retrieves detailed information about a specific process,
    including all its relationships.

    Raises 404 if process not found.
    """
    return await service.get_process_by_id(process_id)


@router.put("/{process_id}", response_model=ProcessResponse)
async def update_process(
    process_id: int,
    process_in: ProcessUpdate,
    service: ProcessServiceDep,
):
    """
    Update an existing process.

    Updates process attributes and/or relationships.
    Supports partial updates (only specified fields will be updated).

    Returns the updated process with all details.
    Raises 404 if process not found.
    """
    return await service.update_process(process_id, process_in)


@router.delete("/{process_id}", status_code=status.HTTP_200_OK)
async def delete_process(
    process_id: int,
    service: ProcessServiceDep,
):
    """
    Delete a process.

    Completely removes a process and its relationships.
    This operation cannot be undone.

    Returns a success message.
    Raises 404 if process not found.
    """
    await service.delete_process(process_id)
    return {"message": "Process deleted successfully"}
