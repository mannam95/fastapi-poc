from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Nested schemas for related entities
class UserInfo(BaseModel):
    """
    Simplified user information schema for nested responses.
    Contains only essential user attributes for display in department contexts.
    """

    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessInfo(BaseModel):
    """
    Simplified process information schema for nested responses.
    Contains only the basic process attributes needed in department contexts.
    """

    id: int
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# Main schemas
class DepartmentBase(BaseModel):
    """
    Base schema for Department with common attributes.
    Defines the core field (title) shared by all department schemas.
    """

    title: str


class DepartmentCreate(DepartmentBase):
    """
    Schema for creating a new department.
    Extends the base schema with creator ID and optional process associations.
    """

    created_by_id: int
    process_ids: List[int] = []


class DepartmentUpdate(BaseModel):
    """
    Schema for updating a department.
    All fields are optional to support partial updates of attributes
    and process relationships.
    """

    title: Optional[str] = None
    process_ids: List[int] = []


class DepartmentResponse(DepartmentBase):
    """
    Schema for reading department data.
    Provides a complete representation of a department including relationships
    with users and processes for API responses.
    """

    id: int
    created_at: datetime
    created_by_id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = []

    class Config:
        from_attributes = True
