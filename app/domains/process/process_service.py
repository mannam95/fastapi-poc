# app/domains/process/process_service.py
# This file contains the business logic for the process domain

from asyncio import TaskGroup
from typing import Any, List, Optional, Protocol, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.async_database import AsyncDatabaseSessionManager
from app.core.exceptions import NotFoundException, RelationshipException
from app.core.logging_service import BaseLoggingService
from app.domains.department.department_model import Department
from app.domains.location.location_model import Location
from app.domains.process.process_model import Process
from app.domains.process.process_schemas import ProcessCreate, ProcessUpdate
from app.domains.resource.resource_model import Resource
from app.domains.role.role_model import Role
from app.domains.shared.base_service import BaseService
from app.domains.user.user_model import User

# ModelType = Type[DeclarativeBase]


class HasID(Protocol):
    id: Any


# Type variable for SQLAlchemy models with ID constraint
ModelType = TypeVar("ModelType", bound=HasID)


class ProcessService(BaseService):
    """Service for process-related operations"""

    def __init__(
        self,
        session: AsyncSession,
        async_db_session_manager: AsyncDatabaseSessionManager,
        logging_service: BaseLoggingService,
    ):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, async_db_session_manager, logging_service)

    async def _get_process_m2m_relationships(
        self,
        department_ids: Optional[List[int]] = None,
        location_ids: Optional[List[int]] = None,
        resource_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None,
    ) -> tuple[List[Department], List[Location], List[Resource], List[Role]]:
        """
        Fetch all many-to-many relationships concurrently using TaskGroup.

        Args:
            department_ids: List of department IDs
            location_ids: List of location IDs
            resource_ids: List of resource IDs
            role_ids: List of role IDs

        Returns:
            Tuple of (departments, locations, resources, roles)

        Raises:
            RelationshipException: If any of the IDs don't exist
        """
        async with TaskGroup() as tg:
            # Create tasks for each relationship type
            departments_task = tg.create_task(
                self._get_entities_by_ids(Department, department_ids or [])
            )
            locations_task = tg.create_task(self._get_entities_by_ids(Location, location_ids or []))
            resources_task = tg.create_task(self._get_entities_by_ids(Resource, resource_ids or []))
            roles_task = tg.create_task(self._get_entities_by_ids(Role, role_ids or []))

        # Return all results
        return (
            departments_task.result(),
            locations_task.result(),
            resources_task.result(),
            roles_task.result(),
        )

    async def _get_entities_by_ids(
        self, model_class: Type[ModelType], ids: List[int]
    ) -> List[ModelType]:
        """
        Get entities by their IDs.

        Args:
            model_class: The SQLAlchemy model class
            ids: List of IDs to fetch

        Returns:
            List of entities

        Raises:
            RelationshipException: If any IDs don't exist
        """
        if not ids:
            return []

        db_session = self.async_db_session_manager.get_session()
        try:
            result = await db_session.execute(select(model_class).where(model_class.id.in_(ids)))
            entities = list(result.scalars().all())

            # Validate all IDs exist
            found_ids = {entity.id for entity in entities}
            missing_ids = set(ids) - found_ids
            if missing_ids:
                entity_name = model_class.__name__
                raise RelationshipException(f"Some {entity_name} IDs not found: {missing_ids}")

            # Detach all entities from the session
            for entity in entities:
                db_session.expunge(entity)

            return entities
        except Exception as ex:
            print(f"Exception in _get_entities_by_ids: {ex}")
            raise ex
        finally:
            await db_session.close()

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
        # Fetch all relationships concurrently
        departments, locations, resources, roles = await self._get_process_m2m_relationships(
            department_ids=process_data.department_ids,
            location_ids=process_data.location_ids,
            resource_ids=process_data.resource_ids,
            role_ids=process_data.role_ids,
        )

        created_by_user = await self.session.get(User, 1)

        # Create new Process instance with relationships
        db_process = Process(
            title=process_data.title,
            description=process_data.description,
            created_by_id=1,
            created_by=created_by_user,
            # departments=[await self.session.merge(dept) for dept in departments],
            # locations=[await self.session.merge(loc) for loc in locations],
            # resources=[await self.session.merge(res) for res in resources],
            # roles=[await self.session.merge(role) for role in roles],
        )

        try:
            # Add the process to the database
            self.session.add(db_process)

            # add the departments, locations, resources, and roles to the process
            db_process.departments = [await self.session.merge(dept) for dept in departments]
            db_process.locations = [await self.session.merge(loc) for loc in locations]
            db_process.resources = [await self.session.merge(res) for res in resources]
            db_process.roles = [await self.session.merge(role) for role in roles]

            # Commit the process to the database
            await self.session.commit()

            # refresh the process to get the latest data
            await self.session.refresh(db_process)
        except Exception as ex:
            print(f"Process created_by: {db_process.created_by_id}")
            print(f"Exception in create_process: {ex}")
            raise ex

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
        # Get the process by ID
        process = await self.session.get(Process, process_id)
        if not process:
            raise NotFoundException(f"Process with ID {process_id} not found")

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

        # refresh the process to get the latest data
        await self.session.refresh(process)

        # Log the update event
        await self.logging_service.log_business_event(
            "process_updated",
            {
                "process_id": process_id,
                "updated_fields": update_data,
                "department_ids": process_data.department_ids,
                "location_ids": process_data.location_ids,
                "resource_ids": process_data.resource_ids,
                "role_ids": process_data.role_ids,
            },
        )

        # return the process
        return process

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

        Raises:
            RelationshipException: If there's an issue with the relationship operations
        """
        try:
            async with TaskGroup() as task_group:
                if department_ids is not None:
                    task_group.create_task(
                        self._update_relationship_with_new_session(
                            process.departments, Department, department_ids
                        )
                    )
                if location_ids is not None:
                    task_group.create_task(
                        self._update_relationship_with_new_session(
                            process.locations, Location, location_ids
                        )
                    )
                if resource_ids is not None:
                    task_group.create_task(
                        self._update_relationship_with_new_session(
                            process.resources, Resource, resource_ids
                        )
                    )
                if role_ids is not None:
                    task_group.create_task(
                        self._update_relationship_with_new_session(process.roles, Role, role_ids)
                    )
        except Exception as ex:
            # Extract the first exception from the group
            print(f"Exception in _update_relationships: {ex}")
            if isinstance(ex, RelationshipException):
                raise ex
            raise RelationshipException(f"Failed to update relationships: {str(ex)}") from ex

    async def _update_relationship_with_new_session(
        self,
        relationship_collection: List[Any],
        model_class: Type[ModelType],
        related_ids: List[int],
    ) -> None:
        """
        Update a relationship using a new scoped session.

        Args:
            relationship_collection: The collection to update
            model_class: The class of the related entity
            related_ids: List of IDs to set as the new relationship values
        """
        # Get a new scoped session for this task
        new_session = self.async_db_session_manager.get_session()
        try:
            # Get current IDs for comparison
            current_ids = [item.id for item in relationship_collection]

            # Determine what needs to be added or removed
            ids_to_add = set(related_ids) - set(current_ids)
            ids_to_remove = set(current_ids) - set(related_ids)

            # Remove items not in the new list
            if ids_to_remove:
                items_to_remove = [
                    item for item in relationship_collection if item.id in ids_to_remove
                ]
                for item in items_to_remove:
                    relationship_collection.remove(item)

            # Add new items
            if ids_to_add:
                # Get entities using the new session
                result = await new_session.execute(
                    select(model_class).where(model_class.id.in_(list(ids_to_add)))
                )
                entities_to_add = list(result.scalars().all())

                # Validate all IDs exist
                found_ids = {entity.id for entity in entities_to_add}
                missing_ids = set(ids_to_add) - found_ids
                if missing_ids:
                    entity_name = model_class.__name__
                    raise RelationshipException(f"Some {entity_name} IDs not found: {missing_ids}")

                # Use merge to handle objects across sessions
                for entity in entities_to_add:
                    # Detach from current session
                    new_session.expunge(entity)
                    # Merge into the parent object's session
                    merged_entity = await self.session.merge(entity)
                    relationship_collection.append(merged_entity)
        except Exception as ex:
            print(f"Exception in _update_relationship_with_new_session: {ex}")
            raise ex
        finally:
            # Ensure the session is closed
            await new_session.close()
