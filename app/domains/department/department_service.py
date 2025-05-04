# app/domains/department/department_service.py
# This file contains the business logic for the department domain

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.department.department_model import Department
from app.domains.department.department_schemas import DepartmentCreate, DepartmentUpdate
from app.domains.process.process_model import Process
from app.domains.shared.service.base_service import BaseService
from app.utils.exceptions import NotFoundException
from app.utils.logging_service import BaseLoggingService


class DepartmentService(BaseService):
    """Service for department-related operations"""

    def __init__(self, session: AsyncSession, logging_service: BaseLoggingService):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, logging_service)

    async def create_department(self, department_data: DepartmentCreate) -> Department:
        """
        Create a new department with optional process relationships.

        Creates a department record and establishes relationships with
        processes based on provided IDs.

        Args:
            department_data: Data for creating the department, including title,
                             creator ID, and optional process relationship IDs

        Returns:
            Department: The newly created department with all relationships loaded

        Raises:
            DatabaseException: If there's a database error
            RelationshipException: If related entities don't exist
        """
        # Create new Department instance from input data
        db_department = Department(
            title=department_data.title, created_by_id=department_data.created_by_id
        )

        # Add the department to the database to get an ID
        self.session.add(db_department)

        # Handle relationships
        await self._update_relationships(db_department, department_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the department to get the latest data
        await self.session.refresh(db_department)

        # Log the creation event
        await self.logging_service.log_business_event(
            "department_created",
            {
                "department_id": db_department.id,
                "title": db_department.title,
                "created_by": db_department.created_by_id,
                "process_ids": department_data.process_ids,
            },
        )

        # return the department
        return db_department

    async def get_departments(self, offset: int = 0, limit: int = 100) -> List[Department]:
        """
        Get a list of departments with pagination and eager loading of relationships.

        Retrieves departments with their associated creator and process relationships
        using SQLAlchemy's selectinload for efficient eager loading.

        Args:
            offset: Number of records to offset for pagination
            limit: Maximum number of records to return

        Returns:
            List[Department]: List of department objects with relationships loaded

        Raises:
            DatabaseException: If there's a database error
        """
        # Get the departments with associated data
        result = await self.session.execute(
            select(Department)
            .options(selectinload(Department.created_by), selectinload(Department.processes))
            .offset(offset)
            .limit(limit)
        )

        # Convert the result to a list of departments
        departments = list(result.scalars().all())

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "departments_retrieved",
            {
                "count": len(departments),
                "offset": offset,
                "limit": limit,
            },
        )

        # return the departments
        return departments

    async def get_department_by_id(self, department_id: int) -> Department:
        """
        Get a single department by ID with all relationships loaded.

        Retrieves a specific department with its associated creator and process
        relationships using efficient eager loading.

        Args:
            department_id: Database ID of the department to retrieve

        Returns:
            Department: The requested department with all relationships loaded

        Raises:
            NotFoundException: If department not found
            DatabaseException: If there's a database error
        """
        # Get the department by ID with associated data
        result = await self.session.execute(
            select(Department)
            .options(selectinload(Department.created_by), selectinload(Department.processes))
            .where(Department.id == department_id)
        )

        # Convert the result to a single department
        department = result.scalars().first()
        if not department:
            raise NotFoundException(f"Department with ID {department_id} not found")

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "department_retrieved",
            {
                "department_id": department_id,
            },
        )

        # return the department
        return department

    async def update_department(
        self, department_id: int, department_data: DepartmentUpdate
    ) -> Department:
        """
        Update an existing department and its relationships.

        Updates department attributes and its relationships with processes.
        Only provided fields will be updated.

        Args:
            department_id: Database ID of the department to update
            department_data: Data for updating the department, including fields to
                             update and process relationship IDs

        Returns:
            Department: The updated department with all relationships

        Raises:
            NotFoundException: If department not found
            DatabaseException: If there's a database error
            RelationshipException: If there's an issue with relationship operations
        """
        # Get the department by ID
        department = await self.session.get(Department, department_id)
        if not department:
            raise NotFoundException(f"Department with ID {department_id} not found")

        # Update department fields
        update_data = department_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Only update if the value is not None
                setattr(department, key, value)

        # Handle relationships
        await self._update_relationships(department, department_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the department to get the latest data
        await self.session.refresh(department)

        # Log the update event
        await self.logging_service.log_business_event(
            "department_updated",
            {
                "department_id": department_id,
                "updated_fields": update_data,
                "process_ids": department_data.process_ids,
            },
        )

        # return the department
        return department

    async def delete_department(self, department_id: int) -> None:
        """
        Delete a department and clear all of its relationships.

        Removes all relationships to processes before deleting the department itself.

        Args:
            department_id: Database ID of the department to delete

        Raises:
            NotFoundException: If department not found
            DatabaseException: If there's a database error
        """
        # Get the department by ID
        department = await self.session.get(Department, department_id)

        if not department:
            raise NotFoundException(f"Department with ID {department_id} not found")

        # Clear all relationships
        department.processes = []

        # Now delete the department
        await self.session.delete(department)

        # Finally commit all
        await self.session.commit()

        # Log the deletion event
        await self.logging_service.log_business_event(
            "department_deleted",
            {
                "department_id": department_id,
            },
        )

    async def _update_relationships(
        self, department: Department, process_ids: Optional[List[int]] = None
    ) -> None:
        """
        Update the many-to-many relationships of a department.

        This method handles adding and removing related entities based on the provided IDs.
        It uses the base service's update_many_to_many_relationship method to efficiently
        update each relationship without completely replacing collections.

        Args:
            department: The department to update
            process_ids: List of process IDs to associate with the department

        Raises:
            RelationshipException: If there's an issue with the relationship operations
        """
        if process_ids is not None:
            await self.update_many_to_many_relationship(department.processes, Process, process_ids)
