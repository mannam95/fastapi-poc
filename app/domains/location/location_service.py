# app/domains/location/location_service.py
# This file contains the business logic for the location domain

from typing import List
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
            update_data = location_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(location, key, value)
            await self.session.commit()
            await self.session.refresh(location, ['created_by', 'processes'])
            return location
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_location(self, location_id: int) -> Location:
        """Delete a location"""
        location = await self.session.get(Location, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        try:
            await self.session.delete(location)
            await self.session.commit()
            return location
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    # Methods for managing process associations
    
    async def add_process_to_location(self, location_id: int, process_id: int) -> Location:
        """Add a process to a location"""
        location = await self.session.get(Location, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
            
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
            
        try:
            location.processes.append(process)
            await self.session.commit()
            await self.session.refresh(location, ['processes'])
            return location
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    async def remove_process_from_location(self, location_id: int, process_id: int) -> Location:
        """Remove a process from a location"""
        location = await self.session.get(Location, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
            
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
            
        try:
            if process in location.processes:
                location.processes.remove(process)
                await self.session.commit()
                await self.session.refresh(location, ['processes'])
            return location
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e)) 