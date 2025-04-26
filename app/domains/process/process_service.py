from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessUpdate


async def get_processes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Process]:
    """Get list of processes"""
    result = await db.execute(
        select(Process)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_process(db: AsyncSession, process_id: UUID) -> Optional[Process]:
    """Get a single process by ID with all relationships loaded"""
    result = await db.execute(
        select(Process)
        .where(Process.id == process_id)
        .options(
            selectinload(Process.departments),
            selectinload(Process.roles),
            selectinload(Process.resources),
            selectinload(Process.locations),
        )
    )
    return result.scalars().first()


async def create_process(
    db: AsyncSession,
    process_in: ProcessCreate,
    created_by_id: Optional[UUID] = None
) -> Process:
    """Create a new process"""
    process_data = process_in.model_dump(exclude={"department_ids", "role_ids", "resource_ids", "location_ids"})
    process = Process(**process_data, created_by_id=created_by_id)
    
    # Add the process to the database to get an ID
    db.add(process)
    await db.flush()
    
    await db.commit()
    await db.refresh(process)
    return process


async def update_process(
    db: AsyncSession,
    process: Process,
    process_in: ProcessUpdate
) -> Process:
    """Update an existing process"""
    update_data = process_in.model_dump(exclude_unset=True, exclude={"department_ids", "role_ids", "resource_ids", "location_ids"})
    
    for field, value in update_data.items():
        setattr(process, field, value)
    
    db.add(process)
    await db.commit()
    await db.refresh(process)
    return process 