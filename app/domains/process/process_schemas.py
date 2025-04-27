from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Nested schema for simplified user info
class UserInfo(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Simplified schemas for related entities
class DepartmentInfo(BaseModel):
    id: int
    title: str
    
    class Config:
        from_attributes = True

class LocationInfo(BaseModel):
    id: int
    title: str
    
    class Config:
        from_attributes = True

class ResourceInfo(BaseModel):
    id: int
    title: str
    
    class Config:
        from_attributes = True

class RoleInfo(BaseModel):
    id: int
    title: str
    
    class Config:
        from_attributes = True

class ProcessCreate(BaseModel):
    title: str
    description: Optional[str] = None
    created_by_id: int
    department_ids: Optional[List[int]] = []
    location_ids: Optional[List[int]] = []
    resource_ids: Optional[List[int]] = []
    role_ids: Optional[List[int]] = []
    
    class Config:
        from_attributes = True

class ProcessUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department_ids: Optional[List[int]] = []
    location_ids: Optional[List[int]] = []
    resource_ids: Optional[List[int]] = []
    role_ids: Optional[List[int]] = []
    
    class Config:
        from_attributes = True

class ProcessResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    created_by: Optional[UserInfo] = None
    departments: List[DepartmentInfo] = []
    locations: List[LocationInfo] = []
    resources: List[ResourceInfo] = []
    roles: List[RoleInfo] = []
    
    class Config:
        from_attributes = True
