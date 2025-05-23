"""
Base Service

This module provides a base service class that other domain services can inherit from.
It includes common functionality like relationship management and database operations.
"""

from typing import Any, List, Protocol, Type, TypeVar

from sqlalchemy import select

from app.domains.shared.service.exception_handling_service import (
    ExceptionHandlingServiceBase,
)
from app.utils.exceptions import RelationshipException


# Define a protocol for models with ID
class HasID(Protocol):
    id: Any


# Type variable for SQLAlchemy models with ID constraint
ModelType = TypeVar("ModelType", bound=HasID)
T = TypeVar("T")


class BaseService(ExceptionHandlingServiceBase):
    """
    Base class for all service classes providing common functionality.

    This class extends the ExceptionHandlingServiceBase and adds common
    methods for CRUD operations and relationship management.
    All service classes should inherit from this class.
    """

    async def get_entities_by_ids(
        self, model_class: Type[ModelType], ids: List[int]
    ) -> List[ModelType]:
        """
        Get entities by their IDs with validation.

        This method retrieves entities by their IDs and validates that all requested
        IDs exist in the database. If any IDs are not found, it raises an exception.

        Args:
            model_class: SQLAlchemy model class
            ids: List of entity IDs to retrieve

        Returns:
            List of entity instances corresponding to the provided IDs

        Raises:
            NotFoundException: If any of the requested IDs don't exist in the database
        """
        # Get entities by their IDs
        result = await self.session.execute(select(model_class).where(model_class.id.in_(ids)))

        # Convert the result to a list of entities
        entities = list(result.scalars().all())

        # Check if any IDs were not found
        found_ids = {entity.id for entity in entities}

        # Determine which IDs were not found
        missing_ids = set(ids) - found_ids

        if missing_ids:
            entity_name = model_class.__name__
            raise RelationshipException(f"Some {entity_name} IDs not found: {missing_ids}")

        return entities

    async def update_many_to_many_relationship(
        self,
        relationship_collection: List[Any],
        model_class: Type[ModelType],
        related_ids: List[int],
    ) -> None:
        """
        Update a many-to-many relationship collection.

        Efficiently updates a many-to-many relationship by adding new relations
        and removing no longer needed ones.

        Args:
            relationship_collection: The collection to update (e.g., department.processes)
            model_class: The class of the related entity (e.g., Process)
            related_ids: List of IDs to set as the new relationship values

        Raises:
            RelationshipException: If related entity doesn't exist
        """
        # Get current IDs for comparison
        current_ids = [item.id for item in relationship_collection]

        # Determine what needs to be added or removed
        ids_to_add = set(related_ids) - set(current_ids)

        # Bulk insert new items
        new_entities = await self.get_entities_by_ids(model_class, list(ids_to_add))
        relationship_collection[:] = new_entities
