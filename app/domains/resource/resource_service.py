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
from app.domains.shared.base_service import BaseService


class ResourceService(BaseService):
    """Service for resource-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        super().__init__(session)

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
            
            # Handle relationships
            await self._update_relationships(db_resource, resource_data.process_ids)

            # Finally commit all
            await self.session.commit()

            # refresh the resource to get the id
            await self.session.refresh(db_resource)

            # return the resource
            return db_resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_resources(self, offset: int = 0, limit: int = 100) -> List[Resource]:
        """Get a list of resources with pagination and associated data"""
        # Get the resources with associated data
        result = await self.session.execute(
            select(Resource)
            .options(
                selectinload(Resource.created_by),
                selectinload(Resource.processes)
            )
            .offset(offset)
            .limit(limit)
        )

        # Convert the result to a list of resources
        resources = result.scalars().all()

        # return the resources
        return resources

    async def get_resource_by_id(self, resource_id: int) -> Resource:
        """Get a single resource by ID with associated data"""
        # Get the resource by ID with associated data
        result = await self.session.execute(
            select(Resource)
            .options(
                selectinload(Resource.created_by),
                selectinload(Resource.processes)
            )
            .where(Resource.id == resource_id)
        )

        # Convert the result to a single resource
        resource = result.scalars().first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        # return the resource
        return resource

    async def update_resource(self, resource_id: int, resource_data: ResourceUpdate) -> Resource:
        """Update an existing resource"""
        # Get the resource by ID
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        try:
            # Update resource fields
            update_data = resource_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(resource, key, value)
            
            # Handle relationships
            await self._update_relationships(resource, resource_data.process_ids)
                
            # Finally commit all
            await self.session.commit()

            # refresh the resource to get the id
            await self.session.refresh(resource)

            # return the resource
            return resource
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_resource(self, resource_id: int) -> None:
        """Delete a resource and clear all of its relationships"""
        # Get the resource by ID
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        try:
            # Clear all relationships
            resource.processes = []
            
            # Now delete the resource
            await self.session.delete(resource)

            # Finally commit all
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    async def _update_relationships(self, resource: Resource, process_ids: List[int]) -> None:
        """Update the many-to-many relationships of a resource
        
        This method handles adding and removing related entities based on the provided IDs.
        
        Args:
            resource: The resource to update
            process_ids: List of process IDs to associate with the resource
        """
        if process_ids is not None:
            await self.update_many_to_many_relationship(
                resource.processes, 
                Process, 
                process_ids
            )
            
        await self.session.commit()
        await self.session.refresh(resource) 