# app/domains/location/location_service.py
# This file contains the business logic for the location domain

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.location.location_model import Location
from app.domains.location.location_schemas import LocationCreate, LocationUpdate
from app.domains.process.process_model import Process
from app.domains.shared.service.base_service import BaseService
from app.utils.exceptions import NotFoundException
from app.utils.logging_service import BaseLoggingService


class LocationService(BaseService):
    """Service for location-related operations"""

    def __init__(self, session: AsyncSession, logging_service: BaseLoggingService):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, logging_service)

    async def create_location(self, location_data: LocationCreate) -> Location:
        """
        Create a new location with optional process relationships.

        Creates a location record and establishes relationships with
        processes based on provided IDs.

        Args:
            location_data: Data for creating the location, including title,
                           creator ID, and optional process relationship IDs

        Returns:
            Location: The newly created location with all relationships loaded

        Raises:
            DatabaseException: If there's a database error
            RelationshipException: If related entities don't exist
        """
        # Create new Location instance from input data
        db_location = Location(title=location_data.title, created_by_id=location_data.created_by_id)

        # Add the location to the database to get an ID
        self.session.add(db_location)

        # Handle processes if provided
        await self._update_relationships(db_location, location_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the location to get the latest data
        await self.session.refresh(db_location)

        # Log the creation event
        await self.logging_service.log_business_event(
            "location_created",
            {
                "location_id": db_location.id,
                "title": db_location.title,
                "created_by": db_location.created_by_id,
                "process_ids": location_data.process_ids,
            },
        )

        # return the location
        return db_location

    async def get_locations(self, offset: int = 0, limit: int = 100) -> List[Location]:
        """
        Get a list of locations with pagination and eager loading of relationships.

        Retrieves locations with their associated creator and process relationships
        using SQLAlchemy's selectinload for efficient eager loading.

        Args:
            offset: Number of records to offset for pagination
            limit: Maximum number of records to return

        Returns:
            List[Location]: List of location objects with relationships loaded

        Raises:
            DatabaseException: If there's a database error
        """
        # Get the locations with associated data
        result = await self.session.execute(
            select(Location)
            .options(selectinload(Location.created_by), selectinload(Location.processes))
            .offset(offset)
            .limit(limit)
        )

        # Convert the result to a list of locations
        locations = list(result.scalars().all())

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "locations_retrieved",
            {
                "count": len(locations),
                "offset": offset,
                "limit": limit,
            },
        )

        # return the locations
        return locations

    async def get_location_by_id(self, location_id: int) -> Location:
        """
        Get a single location by ID with all relationships loaded.

        Retrieves a specific location with its associated creator and process
        relationships using efficient eager loading.

        Args:
            location_id: Database ID of the location to retrieve

        Returns:
            Location: The requested location with all relationships loaded

        Raises:
            NotFoundException: If location not found
            DatabaseException: If there's a database error
        """
        # Get the location by ID with associated data
        result = await self.session.execute(
            select(Location)
            .options(selectinload(Location.created_by), selectinload(Location.processes))
            .where(Location.id == location_id)
        )

        # Convert the result to a single location
        location = result.scalars().first()
        if not location:
            raise NotFoundException(f"Location with ID {location_id} not found")

        # Log the retrieval event
        await self.logging_service.log_business_event(
            "location_retrieved",
            {
                "location_id": location_id,
            },
        )

        # return the location
        return location

    async def update_location(self, location_id: int, location_data: LocationUpdate) -> Location:
        """
        Update an existing location and its relationships.

        Updates location attributes and its relationships with processes.
        Only provided fields will be updated.

        Args:
            location_id: Database ID of the location to update
            location_data: Data for updating the location, including fields to
                           update and process relationship IDs

        Returns:
            Location: The updated location with all relationships

        Raises:
            NotFoundException: If location not found
            DatabaseException: If there's a database error
            RelationshipException: If there's an issue with relationship operations
        """
        # Get the location by ID
        location = await self.session.get(Location, location_id)
        if not location:
            raise NotFoundException(f"Location with ID {location_id} not found")

        # Update location fields
        update_data = location_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Only update if the value is not None
                setattr(location, key, value)

        # Handle relationships
        await self._update_relationships(location, location_data.process_ids)

        # Finally commit all
        await self.session.commit()

        # refresh the location to get the latest data
        await self.session.refresh(location)

        # Log the update event
        await self.logging_service.log_business_event(
            "location_updated",
            {
                "location_id": location_id,
                "updated_fields": update_data,
                "process_ids": location_data.process_ids,
            },
        )

        # return the location
        return location

    async def delete_location(self, location_id: int) -> None:
        """
        Delete a location and clear all of its relationships.

        Removes all relationships to processes before deleting the location itself.

        Args:
            location_id: Database ID of the location to delete

        Raises:
            NotFoundException: If location not found
            DatabaseException: If there's a database error
        """
        # Get the location by ID
        location = await self.session.get(Location, location_id)
        if not location:
            raise NotFoundException(f"Location with ID {location_id} not found")

        # Clear all relationships
        location.processes = []

        # Now delete the location
        await self.session.delete(location)

        # Finally commit all
        await self.session.commit()

        # Log the deletion event
        await self.logging_service.log_business_event(
            "location_deleted",
            {
                "location_id": location_id,
            },
        )

    async def _update_relationships(
        self, location: Location, process_ids: Optional[List[int]]
    ) -> None:
        """
        Update the many-to-many relationships of a location.

        This method handles adding and removing related entities based on the provided IDs.
        It uses the base service's update_many_to_many_relationship method to efficiently
        update each relationship without completely replacing collections.

        Args:
            location: The location to update
            process_ids: List of process IDs to associate with the location

        Raises:
            RelationshipException: If there's an issue with the relationship operations
        """
        if process_ids is not None:
            await self.update_many_to_many_relationship(location.processes, Process, process_ids)
