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
class DepartmentBase(BaseModel):
    """Base schema for Department"""
    title: str

class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department"""
    created_by_id: int

class DepartmentRead(DepartmentBase):
    """Schema for reading department data"""
    id: int
    created_at: datetime
    created_by_id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = []
    
    class Config:
        from_attributes = True

class DepartmentUpdate(BaseModel):
    """Schema for updating a department"""
    title: Optional[str] = None

# Schema for adding/removing process associations
class DepartmentProcessAssociation(BaseModel):
    process_id: int 