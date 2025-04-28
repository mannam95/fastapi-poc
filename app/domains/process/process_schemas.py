from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Nested schema for simplified user info
class UserInfo(BaseModel):
    """
    Simplified user information schema used in nested responses.
    Contains only essential user attributes for display purposes.
    """

    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


# Simplified schemas for related entities
class DepartmentInfo(BaseModel):
    """
    Simplified department information for use in nested responses.
    Contains only the essential department attributes.
    """

    id: int
    title: str

    class Config:
        from_attributes = True


class LocationInfo(BaseModel):
    """
    Simplified location information for use in nested responses.
    Contains only the essential location attributes.
    """

    id: int
    title: str

    class Config:
        from_attributes = True


class ResourceInfo(BaseModel):
    """
    Simplified resource information for use in nested responses.
    Contains only the essential resource attributes.
    """

    id: int
    title: str

    class Config:
        from_attributes = True


class RoleInfo(BaseModel):
    """
    Simplified role information for use in nested responses.
    Contains only the essential role attributes.
    """

    id: int
    title: str

    class Config:
        from_attributes = True


class ProcessCreate(BaseModel):
    """
    Schema for creating a new process.
    Includes required fields and optional relationships to other entities.
    """

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
    """
    Schema for updating an existing process.
    All fields are optional to support partial updates.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    department_ids: Optional[List[int]] = []
    location_ids: Optional[List[int]] = []
    resource_ids: Optional[List[int]] = []
    role_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True


class ProcessResponse(BaseModel):
    """
    Schema for process data in API responses.
    Includes full process details with nested related entities.
    """

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
