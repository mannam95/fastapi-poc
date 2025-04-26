# app/domains/resource/resource_service.py
# This file contains the business logic for the resource domain

from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.resource.resource_model import Resource
from app.domains.resource.resource_schemas import ResourceCreate, ResourceUpdate
from app.domains.process.process_model import Process


class ResourceService:
    """Service for resource-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_resource(self, resource_data: ResourceCreate) -> Resource:
        """Create a new resource"""
        try:
            # Create new Resource instance from input data
            db_resource = Resource(
                title=resource_data.title,
                created_by_id=resource_data.created_by_id
            )
            
            # Add the resource to the database to get an ID
            self.session.add(db_resource)    
            await self.session.commit()
            await self.session.refresh(db_resource)
            return db_resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_resources(self, offset: int = 0, limit: int = 100) -> List[Resource]:
        """Get a list of resources with pagination and associated data"""
        result = await self.session.execute(
            select(Resource)
            .options(
                selectinload(Resource.created_by),
                selectinload(Resource.processes)
            )
            .offset(offset)
            .limit(limit)
        )
        resources = result.scalars().all()
        return resources

    async def get_resource_by_id(self, resource_id: int) -> Resource:
        """Get a single resource by ID with associated data"""
        result = await self.session.execute(
            select(Resource)
            .options(
                selectinload(Resource.created_by),
                selectinload(Resource.processes)
            )
            .where(Resource.id == resource_id)
        )
        resource = result.scalars().first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource

    async def update_resource(self, resource_id: int, resource_data: ResourceUpdate) -> Resource:
        """Update an existing resource"""
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        try:
            update_data = resource_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(resource, key, value)
            await self.session.commit()
            await self.session.refresh(resource, ['created_by', 'processes'])
            return resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_resource(self, resource_id: int) -> Resource:
        """Delete a resource"""
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        try:
            await self.session.delete(resource)
            await self.session.commit()
            return resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    # Methods for managing process associations
    
    async def add_process_to_resource(self, resource_id: int, process_id: int) -> Resource:
        """Add a process to a resource"""
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
            
        try:
            resource.processes.append(process)
            await self.session.commit()
            await self.session.refresh(resource, ['processes'])
            return resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    async def remove_process_from_resource(self, resource_id: int, process_id: int) -> Resource:
        """Remove a process from a resource"""
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
            
        try:
            if process in resource.processes:
                resource.processes.remove(process)
                await self.session.commit()
                await self.session.refresh(resource, ['processes'])
            return resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e)) 