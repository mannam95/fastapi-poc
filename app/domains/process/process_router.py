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
async def create_new_process(service: ProcessServiceDep, process_in: ProcessCreate):
    """Create a new process"""
    return await service.create_process(process_in)


@router.get("/", response_model=List[ProcessResponse])
async def read_processes(
    service: ProcessServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    """Get list of processes"""
    return await service.get_processes(offset, limit)


@router.get("/{process_id}", response_model=ProcessResponse)
async def read_process(
    process_id: int,
    service: ProcessServiceDep,
):
    """Get a single process by ID with all relationships loaded"""
    return await service.get_process_by_id(process_id)


@router.put("/{process_id}", response_model=ProcessResponse)
async def update_process(
    process_id: int,
    process_in: ProcessUpdate,
    service: ProcessServiceDep,
):
    """Update an existing process"""
    return await service.update_process(process_id, process_in)


@router.delete("/{process_id}", status_code=status.HTTP_200_OK)
async def delete_process(
    process_id: int,
    service: ProcessServiceDep,
):
    """Delete a process and clear all of its relationships"""
    await service.delete_process(process_id)
    return {"message": "Process deleted successfully"}
