"""
Base Service

This module provides a base service class that other domain services can inherit from.
It includes common functionality like relationship management and database operations.
"""

from typing import List, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.collections import InstrumentedList

# Type variable for SQLAlchemy models
ModelType = TypeVar("ModelType")
T = TypeVar("T")


class BaseService:
    """
    Base service class for domain services.

    This class provides common functionality for database operations,
    entity retrieval, and relationship management.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the service with a database session.

        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

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
            HTTPException: If any of the requested IDs don't exist in the database
        """
        try:
            # Get entities by their IDs
            result = await self.session.execute(select(model_class).where(model_class.id.in_(ids)))

            # Convert the result to a list of entities
            entities = result.scalars().all()

            # Check if any IDs were not found
            found_ids = {entity.id for entity in entities}

            # Determine which IDs were not found
            missing_ids = set(ids) - found_ids

            if missing_ids:
                entity_name = model_class.__name__
                raise HTTPException(
                    status_code=404,
                    detail=f"Some {entity_name} IDs not found: {missing_ids}",
                )

            return entities
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def update_many_to_many_relationship(
        self,
        current_collection: InstrumentedList,
        model_class: Type[ModelType],
        new_ids: List[int],
    ) -> None:
        """
        Update a many-to-many relationship collection efficiently.

        This method updates a SQLAlchemy relationship collection by adding new entities
        and removing ones that are no longer needed, without replacing the entire collection.
        This is more efficient than clearing and rebuilding the collection when only a few
        items need to change.

        Args:
            current_collection: The current relationship collection (e.g., role.processes)
            model_class: The SQLAlchemy model class of the related entities
            new_ids: The new IDs to set in the relationship

        Raises:
            HTTPException: If any of the new_ids don't correspond to existing entities
        """
        if not new_ids:
            # If empty list provided, clear all relationships
            current_collection.clear()
            return

        # Get current IDs in the relationship
        current_ids = {entity.id for entity in current_collection}

        # Determine which IDs to add
        ids_to_add = set(new_ids) - current_ids

        # Determine which IDs to remove
        ids_to_remove = current_ids - set(new_ids)

        # Only fetch entities that need to be added
        if ids_to_add:
            entities_to_add = await self.get_entities_by_ids(model_class, list(ids_to_add))
            for entity in entities_to_add:
                current_collection.append(entity)

        # Remove entities that are no longer needed
        if ids_to_remove:
            current_collection[:] = [
                entity for entity in current_collection if entity.id not in ids_to_remove
            ]
