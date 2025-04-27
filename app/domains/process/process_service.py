# app/domains/process/process_service.py
# This file contains the business logic for the process domain

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessUpdate
from app.domains.department.department_model import Department
from app.domains.location.location_model import Location
from app.domains.resource.resource_model import Resource
from app.domains.role.role_model import Role


class ProcessService:
    """Service for process-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_process(self, process_data: ProcessCreate) -> Process:
        """Create a new process with optional related entities"""
        try:
            db_process = Process(
                title=process_data.title,
                description=process_data.description,
                created_by_id=process_data.created_by_id
            )

            self.session.add(db_process)

            # Handle relationships
            await self._update_relationships(
                db_process,
                department_ids=process_data.department_ids,
                location_ids=process_data.location_ids,
                resource_ids=process_data.resource_ids,
                role_ids=process_data.role_ids
            )

            # Finally commit all
            await self.session.commit()

            # refresh the process to get the id
            await self.session.refresh(db_process)
            return db_process
        
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_processes(self, offset: int = 0, limit: int = 100) -> List[Process]:
        """Get a list of processes with pagination and associated user data"""
        result = await self.session.execute(
            select(Process)
            .options(
                selectinload(Process.created_by),
                selectinload(Process.departments),
                selectinload(Process.locations),
                selectinload(Process.resources),
                selectinload(Process.roles)
            )
            .offset(offset)
            .limit(limit)
        )
        processes = result.scalars().all()
        return processes

    async def get_process_by_id(self, process_id: int) -> Process:
        """Get a single process by ID with associated user data"""
        result = await self.session.execute(
            select(Process)
            .options(
                selectinload(Process.created_by),
                selectinload(Process.departments),
                selectinload(Process.locations),
                selectinload(Process.resources),
                selectinload(Process.roles)
            )
            .where(Process.id == process_id)
        )
        process = result.scalars().first()
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    async def update_process(self, process_id: int, process_data: ProcessUpdate) -> Process:
        """Update an existing process"""
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        try:
            # Update process fields
            update_data = process_data.model_dump(exclude={"department_ids", "location_ids", "resource_ids", "role_ids"}, exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(process, key, value)
            
            # Handle relationships
            await self._update_relationships(
                process,
                department_ids=process_data.department_ids,
                location_ids=process_data.location_ids,
                resource_ids=process_data.resource_ids,
                role_ids=process_data.role_ids
            )
            
            # Commit all changes at once
            await self.session.commit()
            
            # refresh the process to get latest data
            await self.session.refresh(process)
            return process
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_process(self, process_id: int) -> None:
        """Delete a process and clear all of its relationships"""
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        try:
            # Clear all relationships
            process.departments = []
            process.locations = []
            process.resources = []
            process.roles = []
            
            await self.session.delete(process)
            await self.session.commit()
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


    async def _update_relationships(
        self, 
        process: Process, 
        department_ids: Optional[List[int]] = None,
        location_ids: Optional[List[int]] = None,
        resource_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None
    ) -> None:
        """Update the many-to-many relationships of a process
        
        This method handles adding and removing related entities based on the provided IDs.
        """
        if department_ids is not None:
            # Clear existing relationships
            process.departments = []
            
            # Add new relationships
            if department_ids:
                departments = await self._get_entities_by_ids(Department, department_ids)
                process.departments = departments
        
        if location_ids is not None:
            # Clear existing relationships
            process.locations = []
            
            # Add new relationships
            if location_ids:
                locations = await self._get_entities_by_ids(Location, location_ids)
                process.locations = locations
        
        if resource_ids is not None:
            # Clear existing relationships
            process.resources = []
            
            # Add new relationships
            if resource_ids:
                resources = await self._get_entities_by_ids(Resource, resource_ids)
                process.resources = resources
        
        if role_ids is not None:
            # Clear existing relationships
            process.roles = []
            
            # Add new relationships
            if role_ids:
                roles = await self._get_entities_by_ids(Role, role_ids)
                process.roles = roles
        
        await self.session.commit()
        await self.session.refresh(process)


    async def _get_entities_by_ids(self, model_class, ids: List[int]) -> List:
        """Get entities by their IDs
        
        Args:
            model_class: SQLAlchemy model class
            ids: List of entity IDs
            
        Returns:
            List of entity instances
        """
        result = await self.session.execute(
            select(model_class).where(model_class.id.in_(ids))
        )
        entities = result.scalars().all()
        
        # Check if any IDs were not found
        found_ids = {entity.id for entity in entities}
        missing_ids = set(ids) - found_ids
        
        if missing_ids:
            entity_name = model_class.__name__
            raise HTTPException(
                status_code=404, 
                detail=f"Some {entity_name} IDs not found: {missing_ids}"
            )
        
        return entities