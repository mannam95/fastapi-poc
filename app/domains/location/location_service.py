# app/domains/location/location_service.py
# This file contains the business logic for the location domain

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.location.location_model import Location
from app.domains.location.location_schemas import LocationCreate, LocationUpdate
from app.domains.process.process_model import Process


class LocationService:
    """Service for location-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_location(self, location_data: LocationCreate) -> Location:
        """Create a new location"""
        try:
            # Create new Location instance from input data
            db_location = Location(
                title=location_data.title,
                created_by_id=location_data.created_by_id
            )
            
            # Add the location to the database to get an ID
            self.session.add(db_location)    
            await self.session.commit()
            await self.session.refresh(db_location)
            
            # Handle processes if provided
            if location_data.process_ids is not None:
                await self._update_process_relationships(db_location, location_data.process_ids)
                
            return db_location
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_locations(self, offset: int = 0, limit: int = 100) -> List[Location]:
        """Get a list of locations with pagination and associated data"""
        result = await self.session.execute(
            select(Location)
            .options(
                selectinload(Location.created_by),
                selectinload(Location.processes)
            )
            .offset(offset)
            .limit(limit)
        )
        locations = result.scalars().all()
        return locations

    async def get_location_by_id(self, location_id: int) -> Location:
        """Get a single location by ID with associated data"""
        result = await self.session.execute(
            select(Location)
            .options(
                selectinload(Location.created_by),
                selectinload(Location.processes)
            )
            .where(Location.id == location_id)
        )
        location = result.scalars().first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return location

    async def update_location(self, location_id: int, location_data: LocationUpdate) -> Location:
        """Update an existing location"""
        location = await self.session.get(Location, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        try:
            # Update location fields
            update_data = location_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(location, key, value)
            
            # Handle processes if provided
            if location_data.process_ids is not None:
                await self._update_process_relationships(location, location_data.process_ids)
                
            await self.session.commit()
            await self.session.refresh(location)
            return location
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_location(self, location_id: int) -> None:
        """Delete a location and clear all of its relationships"""
        location = await self.session.get(Location, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        try:
            # Clear all relationships first to ensure link table entries are removed
            location.processes = []
            await self.session.commit()
            
            # Now delete the location
            await self.session.delete(location)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    async def _update_process_relationships(self, location: Location, process_ids: List[int]) -> None:
        """Update the processes associated with a location
        
        This replaces all existing associations with the new ones provided.
        
        Args:
            location: The location to update
            process_ids: List of process IDs to associate with the location
        """
        # Clear existing relationships
        location.processes = []
        
        if process_ids:
            # Get all processes by their IDs
            result = await self.session.execute(
                select(Process).where(Process.id.in_(process_ids))
            )
            processes = result.scalars().all()
            
            # Check if any process IDs were not found
            found_ids = {process.id for process in processes}
            missing_ids = set(process_ids) - found_ids
            
            if missing_ids:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Some Process IDs not found: {missing_ids}"
                )
            
            # Update the relationships
            location.processes = processes
            
        await self.session.commit()
        await self.session.refresh(location) 