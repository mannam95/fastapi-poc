# app/domains/process/process_service.py
# This file contains the business logic for the process domain

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.department.department_model import Department
from app.domains.location.location_model import Location
from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessUpdate
from app.domains.resource.resource_model import Resource
from app.domains.role.role_model import Role
from app.domains.shared.base_service import BaseService


class ProcessService(BaseService):
    """Service for process-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
        """
        super().__init__(session)

    async def create_process(self, process_data: ProcessCreate) -> Process:
        """
        Create a new process with optional related entities.

        Creates a process record and establishes relationships with departments,
        locations, resources, and roles based on provided IDs.

        Args:
            process_data: Data for creating the process, including title, description,
                          creator ID, and optional relationship IDs

        Returns:
            Process: The newly created process with all relationships loaded

        Raises:
            HTTPException: If there's a database error or related entities don't exist
        """
        try:
            # Create new Process instance from input data
            db_process = Process(
                title=process_data.title,
                description=process_data.description,
                created_by_id=process_data.created_by_id,
            )

            # Add the process to the database to get an ID
            self.session.add(db_process)

            # Handle relationships
            await self._update_relationships(
                db_process,
                department_ids=process_data.department_ids,
                location_ids=process_data.location_ids,
                resource_ids=process_data.resource_ids,
                role_ids=process_data.role_ids,
            )

            # Finally commit all
            await self.session.commit()

            # refresh the process to get the latest data
            await self.session.refresh(db_process)

            # return the process
            return db_process

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_processes(self, offset: int = 0, limit: int = 100) -> List[Process]:
        """
        Get a list of processes with pagination and eager loading of relationships.

        Retrieves processes with their associated creator and related entities
        (departments, locations, resources, roles) using SQLAlchemy's selectinload
        for efficient eager loading.

        Args:
            offset: Number of records to skip for pagination
            limit: Maximum number of records to return

        Returns:
            List[Process]: List of process objects with relationships loaded
        """
        # Get the processes with associated data
        result = await self.session.execute(
            select(Process)
            .options(
                selectinload(Process.created_by),
                selectinload(Process.departments),
                selectinload(Process.locations),
                selectinload(Process.resources),
                selectinload(Process.roles),
            )
            .offset(offset)
            .limit(limit)
        )

        # Convert the result to a list of processes
        processes = list(result.scalars().all())

        # return the processes
        return processes

    async def get_process_by_id(self, process_id: int) -> Process:
        """
        Get a single process by ID with all relationships loaded.

        Retrieves a specific process with its associated creator and related entities
        (departments, locations, resources, roles) using efficient eager loading.

        Args:
            process_id: Database ID of the process to retrieve

        Returns:
            Process: The requested process with all relationships loaded

        Raises:
            HTTPException: If process not found (404)
        """
        # Get the process by ID with associated data
        result = await self.session.execute(
            select(Process)
            .options(
                selectinload(Process.created_by),
                selectinload(Process.departments),
                selectinload(Process.locations),
                selectinload(Process.resources),
                selectinload(Process.roles),
            )
            .where(Process.id == process_id)
        )

        # Convert the result to a single process
        process = result.scalars().first()
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")

        # return the process
        return process

    async def update_process(self, process_id: int, process_data: ProcessUpdate) -> Process:
        """
        Update an existing process and its relationships.

        Updates process attributes and its relationships with departments,
        locations, resources, and roles. Only provided fields will be updated.

        Args:
            process_id: Database ID of the process to update
            process_data: Data for updating the process, including fields to
                          update and relationship IDs

        Returns:
            Process: The updated process with all relationships

        Raises:
            HTTPException: If process not found (404) or database error (500)
        """
        # Get the process by ID
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        try:
            # Update process fields
            update_data = process_data.model_dump(
                exclude={"department_ids", "location_ids", "resource_ids", "role_ids"},
                exclude_unset=True,
            )
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(process, key, value)

            # Handle relationships
            await self._update_relationships(
                process,
                department_ids=process_data.department_ids,
                location_ids=process_data.location_ids,
                resource_ids=process_data.resource_ids,
                role_ids=process_data.role_ids,
            )

            # Finally commit all
            await self.session.commit()

            # refresh the process to get the id
            await self.session.refresh(process)

            # return the process
            return process
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_process(self, process_id: int) -> None:
        """
        Delete a process and clear all of its relationships.

        Removes all relationships to departments, locations, resources,
        and roles before deleting the process itself.

        Args:
            process_id: Database ID of the process to delete

        Raises:
            HTTPException: If process not found (404) or database error (500)
        """
        # Get the process by ID
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        try:
            # Clear all relationships
            process.departments = []
            process.locations = []
            process.resources = []
            process.roles = []

            # Now delete the process
            await self.session.delete(process)

            # Finally commit all
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
        role_ids: Optional[List[int]] = None,
    ) -> None:
        """
        Update the many-to-many relationships of a process.

        This method handles adding and removing related entities based on the provided IDs.
        It uses the base service's update_many_to_many_relationship method to efficiently
        update each relationship without completely replacing collections.

        Args:
            process: The process to update
            department_ids: List of department IDs to associate with the process
            location_ids: List of location IDs to associate with the process
            resource_ids: List of resource IDs to associate with the process
            role_ids: List of role IDs to associate with the process
        """
        if department_ids is not None:
            await self.update_many_to_many_relationship(
                process.departments, Department, department_ids
            )

        if location_ids is not None:
            await self.update_many_to_many_relationship(process.locations, Location, location_ids)

        if resource_ids is not None:
            await self.update_many_to_many_relationship(process.resources, Resource, resource_ids)

        if role_ids is not None:
            await self.update_many_to_many_relationship(process.roles, Role, role_ids)

        await self.session.commit()
        await self.session.refresh(process)
