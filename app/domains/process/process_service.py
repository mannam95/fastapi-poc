# app/domains/process/process_service.py
# This file contains the business logic for the process domain

from typing import List

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.core.logging_service import BaseLoggingService
from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessUpdate
from app.domains.shared.base_service import BaseService


class ProcessService(BaseService):
    """Service for process-related operations"""

    def __init__(self, session: AsyncSession, logging_service: BaseLoggingService):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, logging_service)

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
            DatabaseException: If there's a database error
            RelationshipException: If related entities don't exist
        """
        params = {
            "title": process_data.title,
            "description": process_data.description,
            "created_by_id": process_data.created_by_id,
            "m2m_roles": process_data.role_ids,
            "m2m_departments": process_data.department_ids,
            "m2m_locations": process_data.location_ids,
            "m2m_resources": process_data.resource_ids,
        }
        result = await self.session.execute(
            select(Process)
            .from_statement(
                text(
                    """
            SELECT * FROM create_process_with_m2m(
                :title,
                :description,
                :created_by_id,
                :m2m_roles,
                :m2m_departments,
                :m2m_locations,
                :m2m_resources)
            """
                )
            )
            .params(**params)
        )

        # Extract the Process object from the result
        db_process = result.scalar_one()

        # Finally commit all
        await self.session.commit()

        # refresh the process to get the latest data
        await self.session.refresh(db_process)

        # Log the creation event
        await self.logging_service.log_business_event(
            "process_created",
            {
                "process_id": db_process.id,
                "title": db_process.title,
                "description": db_process.description,
                "created_by": db_process.created_by_id,
                "department_ids": process_data.department_ids,
                "location_ids": process_data.location_ids,
                "resource_ids": process_data.resource_ids,
                "role_ids": process_data.role_ids,
            },
        )

        # return the process
        return db_process

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

        Raises:
            DatabaseException: If there's a database error
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

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "processes_retrieved",
            {
                "count": len(processes),
                "offset": offset,
                "limit": limit,
            },
        )

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
            NotFoundException: If process not found
            DatabaseException: If there's a database error
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
            raise NotFoundException(f"Process with ID {process_id} not found")

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "process_retrieved",
            {
                "process_id": process_id,
            },
        )

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
            NotFoundException: If process not found
            DatabaseException: If there's a database error
            RelationshipException: If there's an issue with relationship operations
        """
        params = {
            "p_id": process_id,
            "p_title": process_data.title,
            "p_description": process_data.description,
            "m2m_roles": process_data.role_ids,
            "m2m_departments": process_data.department_ids,
            "m2m_locations": process_data.location_ids,
            "m2m_resources": process_data.resource_ids,
        }
        result = await self.session.execute(
            select(Process)
            .from_statement(
                text(
                    """
            SELECT * FROM update_process_with_m2m(
                :p_id,
                :p_title,
                :p_description,
                :m2m_roles,
                :m2m_departments,
                :m2m_locations,
                :m2m_resources)
            """
                )
            )
            .params(**params)
        )

        # Extract the Process object from the result
        db_process = result.scalar_one()

        # Finally commit all
        await self.session.commit()

        # refresh the process to get the latest data
        await self.session.refresh(db_process)

        # Log the update event
        await self.logging_service.log_business_event(
            "process_updated",
            {
                "process_id": process_id,
                "process_title": process_data.title,
                "process_description": process_data.description,
                "department_ids": process_data.department_ids,
                "location_ids": process_data.location_ids,
                "resource_ids": process_data.resource_ids,
                "role_ids": process_data.role_ids,
            },
        )

        # return the process
        return db_process

    async def delete_process(self, process_id: int) -> None:
        """
        Delete a process and clear all of its relationships.

        Removes all relationships to departments, locations, resources,
        and roles before deleting the process itself.

        Args:
            process_id: Database ID of the process to delete

        Raises:
            NotFoundException: If process not found
            DatabaseException: If there's a database error
        """
        # Get the process by ID
        process = await self.session.get(Process, process_id)
        if not process:
            raise NotFoundException(f"Process with ID {process_id} not found")

        # Clear all relationships
        process.departments = []
        process.locations = []
        process.resources = []
        process.roles = []

        # Now delete the process
        await self.session.delete(process)

        # Finally commit all
        await self.session.commit()

        # Log the deletion event
        await self.logging_service.log_business_event(
            "process_deleted",
            {
                "process_id": process_id,
            },
        )
