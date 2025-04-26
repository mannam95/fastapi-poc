from typing import List
from fastapi import APIRouter, status

from app.domains.process.process_schemas import ProcessCreate, ProcessRead, ProcessUpdate
from app.domains.process.process_dependencies import ProcessServiceDep

router = APIRouter()


@router.post("/create-process", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
async def create_new_process(
    service: ProcessServiceDep,
    process_in: ProcessCreate
):
    """Create a new process"""
    return await service.create_process(process_in)


@router.get("/read-processes", response_model=List[ProcessRead])
async def read_processes(
    service: ProcessServiceDep,
    offset: int = 0, 
    limit: int = 100,
):
    """Get list of processes"""
    return await service.get_processes(offset, limit)


@router.get("/read-process/{process_id}", response_model=ProcessRead)
async def read_process(
    process_id: int,
    service: ProcessServiceDep,
):
    """Get a single process by ID with all relationships loaded"""
    return await service.get_process_by_id(process_id)


@router.put("/update-process/{process_id}", response_model=ProcessRead)
async def update_process(
    process_id: int,
    process_in: ProcessUpdate,
    service: ProcessServiceDep,
):
    """Update an existing process"""
    return await service.update_process(process_id, process_in)


@router.delete("/delete-process/{process_id}", response_model=ProcessRead)
async def delete_process(
    process_id: int,
    service: ProcessServiceDep,
):
    """Delete a process"""
    return await service.delete_process(process_id)
    