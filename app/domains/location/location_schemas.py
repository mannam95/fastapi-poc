from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Nested schemas for related entities
class UserInfo(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProcessInfo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# Main schemas
class LocationBase(BaseModel):
    """Base schema for Location"""
    title: str

class LocationCreate(LocationBase):
    """Schema for creating a new location"""
    created_by_id: int

class LocationRead(LocationBase):
    """Schema for reading location data"""
    id: int
    created_at: datetime
    created_by_id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = []
    
    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    """Schema for updating a location"""
    title: Optional[str] = None

# Schema for adding/removing process associations
class LocationProcessAssociation(BaseModel):
    process_id: int 