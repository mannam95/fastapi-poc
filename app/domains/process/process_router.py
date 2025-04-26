from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.database import SessionDep
from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessRead, ProcessUpdate

router = APIRouter()


@router.post("/create-process", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
async def create_new_process(
    session: SessionDep,
    process_in: ProcessCreate
):
    """Create a new process"""
    try:
        # Create new Process instance from input data
        db_process = Process(
            title=process_in.title,
            description=process_in.description
        )
        
        # Add the process to the database to get an ID
        session.add(db_process)    
        session.commit()
        session.refresh(db_process)
        return db_process
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/read-processes", response_model=List[ProcessRead])
async def read_processes(
    session: SessionDep,
    offset: int = 0, 
    limit: int = 100,
):
    """Get list of processes"""
    processes = session.execute(
        select(Process)
        .offset(offset)
        .limit(limit)
    ).scalars().all()
    return processes


@router.get("/read-process/{process_id}", response_model=ProcessRead)
async def read_process(
    process_id: int,
    session: SessionDep,
):
    """Get a single process by ID with all relationships loaded"""
    process = session.get(Process, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    return process


@router.put("/update-process/{process_id}", response_model=ProcessRead)
async def update_process(
    session: SessionDep,
    process_id: int,
    process_in: ProcessUpdate,
):
    """Update an existing process"""
    process = session.get(Process, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    try:
        update_data = process_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Only update if the value is not None
                setattr(process, key, value)
        session.commit()
        session.refresh(process)
        return process
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-process/{process_id}", response_model=ProcessRead)
async def delete_process(
    session: SessionDep,
    process_id: int,
):
    """Delete a process"""
    process = session.get(Process, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    try:
        session.delete(process)
        session.commit()
        return process
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    