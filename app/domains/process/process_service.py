# app/domains/process/process_service.py
# This file contains the business logic for the process domain

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessRead, ProcessUpdate


class ProcessService:
    """Service for process-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_process(self, process_data: ProcessCreate) -> Process:
        """Create a new process"""
        try:
            # Create new Process instance from input data
            db_process = Process(
                title=process_data.title,
                description=process_data.description
            )
            
            # Add the process to the database to get an ID
            self.session.add(db_process)    
            await self.session.commit()
            await self.session.refresh(db_process)
            return db_process
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_processes(self, offset: int = 0, limit: int = 100) -> List[Process]:
        """Get a list of processes with pagination"""
        result = await self.session.execute(
            select(Process)
            .offset(offset)
            .limit(limit)
        )
        processes = result.scalars().all()
        return processes

    async def get_process_by_id(self, process_id: int) -> Process:
        """Get a single process by ID"""
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    async def update_process(self, process_id: int, process_data: ProcessUpdate) -> Process:
        """Update an existing process"""
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        try:
            update_data = process_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(process, key, value)
            await self.session.commit()
            await self.session.refresh(process)
            return process
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_process(self, process_id: int) -> Process:
        """Delete a process"""
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        try:
            await self.session.delete(process)
            await self.session.commit()
            return process
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))