from typing import List, Optional
from pydantic import BaseModel, Field
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
    name: str = Field(..., description="The name of the role")
    description: Optional[str] = Field(None, description="A description of the role")

class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    created_by_id: int
    process_ids: Optional[List[int]] = Field(None, description="IDs of processes to associate with this role")

class RoleUpdate(BaseModel):
    """Schema for updating an existing role"""
    name: Optional[str] = Field(None, description="The name of the role")
    description: Optional[str] = Field(None, description="A description of the role")
    process_ids: Optional[List[int]] = Field(None, description="IDs of processes to associate with this role")

class RoleRead(RoleBase):
    """Schema for reading a role, including its ID and associated processes"""
    id: int = Field(..., description="The ID of the role")
    created_by_id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = Field(default=[], description="List of processes associated with this role")
    
    class Config:
        from_attributes = True 