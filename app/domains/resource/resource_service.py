# app/domains/resource/resource_service.py
# This file contains the business logic for the resource domain

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.core.logging_service import BaseLoggingService
from app.domains.process.process_model import Process
from app.domains.resource.resource_model import Resource
from app.domains.resource.resource_schemas import ResourceCreate, ResourceUpdate
from app.domains.shared.base_service import BaseService


class ResourceService(BaseService):
    """Service for resource-related operations"""

    def __init__(self, session: AsyncSession, logging_service: BaseLoggingService):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, logging_service)

    async def create_resource(self, resource_data: ResourceCreate) -> Resource:
        """
        Create a new resource with optional process relationships.

        Creates a resource record and establishes relationships with
        processes based on provided IDs.

        Args:
            resource_data: Data for creating the resource, including title,
                           creator ID, and optional process relationship IDs

        Returns:
            Resource: The newly created resource with all relationships loaded

        Raises:
            DatabaseException: If there's a database error
            RelationshipException: If related entities don't exist
        """
        # Create new Resource instance from input data
        db_resource = Resource(title=resource_data.title, created_by_id=resource_data.created_by_id)

        # Add the resource to the database to get an ID
        self.session.add(db_resource)

        # Handle relationships
        await self._update_relationships(db_resource, resource_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the resource to get the latest data
        await self.session.refresh(db_resource)

        # Log the creation event
        await self.logging_service.log_business_event(
            "resource_created",
            {
                "resource_id": db_resource.id,
                "title": db_resource.title,
                "created_by": db_resource.created_by_id,
                "process_ids": resource_data.process_ids,
            },
        )

        # return the resource
        return db_resource

    async def get_resources(self, offset: int = 0, limit: int = 100) -> List[Resource]:
        """
        Get a list of resources with pagination and eager loading of relationships.

        Retrieves resources with their associated creator and process relationships
        using SQLAlchemy's selectinload for efficient eager loading.

        Args:
            offset: Number of records to offset for pagination
            limit: Maximum number of records to return

        Returns:
            List[Resource]: List of resource objects with relationships loaded

        Raises:
            DatabaseException: If there's a database error
        """
        # Get the resources with associated data
        result = await self.session.execute(
            select(Resource)
            .options(selectinload(Resource.created_by), selectinload(Resource.processes))
            .offset(offset)
            .limit(limit)
        )

        # Convert the result to a list of resources
        resources = list(result.scalars().all())

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "resources_retrieved",
            {
                "count": len(resources),
                "offset": offset,
                "limit": limit,
            },
        )

        # return the resources
        return resources

    async def get_resource_by_id(self, resource_id: int) -> Resource:
        """
        Get a single resource by ID with all relationships loaded.

        Retrieves a specific resource with its associated creator and process
        relationships using efficient eager loading.

        Args:
            resource_id: Database ID of the resource to retrieve

        Returns:
            Resource: The requested resource with all relationships loaded

        Raises:
            NotFoundException: If resource not found
            DatabaseException: If there's a database error
        """
        # Get the resource by ID with associated data
        result = await self.session.execute(
            select(Resource)
            .options(selectinload(Resource.created_by), selectinload(Resource.processes))
            .where(Resource.id == resource_id)
        )

        # Convert the result to a single resource
        resource = result.scalars().first()
        if not resource:
            raise NotFoundException(f"Resource with ID {resource_id} not found")

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "resource_retrieved",
            {
                "resource_id": resource_id,
            },
        )

        # return the resource
        return resource

    async def update_resource(self, resource_id: int, resource_data: ResourceUpdate) -> Resource:
        """
        Update an existing resource and its relationships.

        Updates resource attributes and its relationships with processes.
        Only provided fields will be updated.

        Args:
            resource_id: Database ID of the resource to update
            resource_data: Data for updating the resource, including fields to
                           update and process relationship IDs

        Returns:
            Resource: The updated resource with all relationships

        Raises:
            NotFoundException: If resource not found
            DatabaseException: If there's a database error
            RelationshipException: If there's an issue with relationship operations
        """
        # Get the resource by ID
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise NotFoundException(f"Resource with ID {resource_id} not found")

        # Update resource fields
        update_data = resource_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Only update if the value is not None
                setattr(resource, key, value)

        # Handle relationships
        await self._update_relationships(resource, resource_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the resource to get the latest data
        await self.session.refresh(resource)

        # Log the update event
        await self.logging_service.log_business_event(
            "resource_updated",
            {
                "resource_id": resource_id,
                "updated_fields": update_data,
                "process_ids": resource_data.process_ids,
            },
        )

        # return the resource
        return resource

    async def delete_resource(self, resource_id: int) -> None:
        """
        Delete a resource and clear all of its relationships.

        Removes all relationships to processes before deleting the resource itself.

        Args:
            resource_id: Database ID of the resource to delete

        Raises:
            NotFoundException: If resource not found
            DatabaseException: If there's a database error
        """
        # Get the resource by ID
        resource = await self.session.get(Resource, resource_id)
        if not resource:
            raise NotFoundException(f"Resource with ID {resource_id} not found")

        # Clear all relationships
        resource.processes = []

        # Now delete the resource
        await self.session.delete(resource)

        # Finally commit all
        await self.session.commit()

        # Log the deletion event
        await self.logging_service.log_business_event(
            "resource_deleted",
            {
                "resource_id": resource_id,
            },
        )

    async def _update_relationships(
        self, resource: Resource, process_ids: Optional[List[int]]
    ) -> None:
        """
        Update the many-to-many relationships of a resource.

        This method handles adding and removing related entities based on the provided IDs.
        It uses the base service's update_many_to_many_relationship method to efficiently
        update each relationship without completely replacing collections.

        Args:
            resource: The resource to update
            process_ids: List of process IDs to associate with the resource

        Raises:
            RelationshipException: If there's an issue with relationship operations
        """
        if process_ids is not None:
            await self.update_many_to_many_relationship(resource.processes, Process, process_ids)
