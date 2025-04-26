from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.process.process_schemas import Process, ProcessCreate, ProcessDetail, ProcessUpdate
from app.domains.process.process_service import create_process, get_process, get_processes, update_process

router = APIRouter()


@router.get("/", response_model=List[Process])
async def read_processes(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of processes"""
    processes = await get_processes(db, skip=skip, limit=limit)
    return processes


@router.get("/{process_id}", response_model=ProcessDetail)
async def read_process(
    process_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a single process"""
    process = await get_process(db, process_id=process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    return process


@router.post("/", response_model=Process, status_code=status.HTTP_201_CREATED)
async def create_new_process(
    process_in: ProcessCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new process"""
    process = await create_process(db=db, process_in=process_in)
    return process


@router.put("/{process_id}", response_model=Process)
async def update_existing_process(
    process_id: UUID,
    process_in: ProcessUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing process"""
    process = await get_process(db, process_id=process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    
    updated_process = await update_process(db=db, process=process, process_in=process_in)
    return updated_process 