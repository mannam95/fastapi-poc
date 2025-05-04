# app/domains/role/role_service.py
# This file contains the service layer for the role domain

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.process.process_model import Process
from app.domains.role.role_model import Role
from app.domains.role.role_schemas import RoleCreate, RoleUpdate
from app.domains.shared.base_service import BaseService
from app.utils.exceptions import NotFoundException
from app.utils.logging_service import BaseLoggingService


class RoleService(BaseService):
    """Service class for handling role-related operations"""

    def __init__(self, session: AsyncSession, logging_service: BaseLoggingService):
        """Initialize the service with a database session and logging service

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, logging_service)

    async def create_role(self, role_data: RoleCreate) -> Role:
        """
        Create a new role with optional process relationships.

        Creates a role record and establishes relationships with
        processes based on provided IDs.

        Args:
            role_data: Data for creating the role, including title,
                       creator ID, and optional process relationship IDs

        Returns:
            Role: The newly created role with all relationships loaded

        Raises:
            DatabaseException: If there's a database error
            RelationshipException: If related entities don't exist
        """
        # Create a new role
        role = Role(title=role_data.title, created_by_id=role_data.created_by_id)

        # Add the role to the database to get an ID
        self.session.add(role)

        # Handle processes if provided
        await self._update_relationships(role, role_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the role to get the latest data
        await self.session.refresh(role)

        # Log the creation
        await self.logging_service.log_business_event(
            "role_created",
            {
                "role_id": role.id,
                "title": role.title,
                "created_by_id": role.created_by_id,
                "process_ids": role_data.process_ids or [],
            },
        )

        # return the role
        return role

    async def get_roles(self, offset: int = 0, limit: int = 100) -> List[Role]:
        """
        Get a list of roles with pagination and eager loading of relationships.

        Retrieves roles with their associated creator and process relationships
        using SQLAlchemy's selectinload for efficient eager loading.

        Args:
            offset: Number of records to offset for pagination
            limit: Maximum number of records to return

        Returns:
            List[Role]: List of role objects with relationships loaded

        Raises:
            DatabaseException: If there's a database error
        """
        # Get the roles with associated data
        query = (
            select(Role)
            .options(selectinload(Role.processes), selectinload(Role.created_by))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)

        # Convert the result to a list of roles
        roles = list(result.scalars().all())

        # Log the retrieval
        await self.logging_service.log_business_event(
            "roles_retrieved",
            {
                "count": len(roles),
                "offset": offset,
                "limit": limit,
            },
        )

        # return the roles
        return roles

    async def get_role_by_id(self, role_id: int) -> Role:
        """
        Get a single role by ID with all relationships loaded.

        Retrieves a specific role with its associated creator and process
        relationships using efficient eager loading.

        Args:
            role_id: Database ID of the role to retrieve

        Returns:
            Role: The requested role with all relationships loaded

        Raises:
            NotFoundException: If role not found
            DatabaseException: If there's a database error
        """
        # Get the role by ID with associated data
        query = (
            select(Role)
            .options(selectinload(Role.processes), selectinload(Role.created_by))
            .where(Role.id == role_id)
        )
        result = await self.session.execute(query)

        # Convert the result to a single role
        role = result.scalars().first()
        if not role:
            raise NotFoundException(f"Role with ID {role_id} not found")

        # Log the retrieval
        await self.logging_service.log_business_event(
            "role_retrieved",
            {
                "role_id": role.id,
                "title": role.title,
                "created_by_id": role.created_by_id,
                "process_count": len(role.processes),
            },
        )

        # return the role
        return role

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """
        Update an existing role and its relationships.

        Updates role attributes and its relationships with processes.
        Only provided fields will be updated.

        Args:
            role_id: Database ID of the role to update
            role_data: Data for updating the role, including fields to
                       update and process relationship IDs

        Returns:
            Role: The updated role with all relationships

        Raises:
            NotFoundException: If role not found
            DatabaseException: If there's a database error
            RelationshipException: If there's an issue with relationship operations
        """
        # Get the role by ID
        role = await self.session.get(Role, role_id)
        if not role:
            raise NotFoundException(f"Role with ID {role_id} not found")

        # Store old values for logging
        old_title = role.title
        old_process_ids = [p.id for p in role.processes]

        # Update the role fields
        update_data = role_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(role, key, value)

        # Handle relationships
        await self._update_relationships(role, role_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the role to get the latest data
        await self.session.refresh(role)

        # Log the update
        await self.logging_service.log_business_event(
            "role_updated",
            {
                "role_id": role.id,
                "old_title": old_title,
                "new_title": role.title,
                "old_process_ids": old_process_ids,
                "new_process_ids": [p.id for p in role.processes],
            },
        )

        # return the role
        return role

    async def delete_role(self, role_id: int) -> None:
        """
        Delete a role and clear all of its relationships.

        Removes all relationships to processes before deleting the role itself.

        Args:
            role_id: Database ID of the role to delete

        Raises:
            NotFoundException: If role not found
            DatabaseException: If there's a database error
        """
        # Get the role by ID
        role = await self.session.get(Role, role_id)
        if not role:
            raise NotFoundException(f"Role with ID {role_id} not found")

        # Store values for logging
        title = role.title
        process_ids = [p.id for p in role.processes]

        # Clear all relationships
        role.processes = []

        # Now delete the role
        await self.session.delete(role)

        # Finally commit all
        await self.session.commit()

        # Log the deletion
        await self.logging_service.log_business_event(
            "role_deleted",
            {
                "role_id": role_id,
                "title": title,
                "process_ids": process_ids,
            },
        )

    async def _update_relationships(self, role: Role, process_ids: Optional[List[int]]) -> None:
        """
        Update the many-to-many relationships of a role.

        This method handles adding and removing related entities based on the provided IDs.
        It uses the base service's update_many_to_many_relationship method to efficiently
        update each relationship without completely replacing collections.

        Args:
            role: The role to update
            process_ids: List of process IDs to associate with the role

        Raises:
            RelationshipException: If there's an issue with relationship operations
        """
        if process_ids is not None:
            await self.update_many_to_many_relationship(role.processes, Process, process_ids)
