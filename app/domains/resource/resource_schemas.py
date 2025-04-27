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
class ResourceBase(BaseModel):
    """Base schema for Resource"""
    title: str

class ResourceCreate(ResourceBase):
    """Schema for creating a new resource"""
    created_by_id: int
    process_ids: Optional[List[int]] = None

class ResourceRead(ResourceBase):
    """Schema for reading resource data"""
    id: int
    created_at: datetime
    created_by_id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = []
    
    class Config:
        from_attributes = True

class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""
    title: Optional[str] = None
    process_ids: Optional[List[int]] = None 