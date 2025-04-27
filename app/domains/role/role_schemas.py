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
class RoleBase(BaseModel):
    """Base schema for Role with common attributes"""
    title: str

class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    created_by_id: int
    process_ids: Optional[List[int]] = []

class RoleUpdate(BaseModel):
    """Schema for updating an existing role"""
    title: Optional[str] = None
    process_ids: Optional[List[int]] = []

class RoleRead(RoleBase):
    """Schema for reading a role, including its ID and associated processes"""
    id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = []
    
    class Config:
        from_attributes = True 