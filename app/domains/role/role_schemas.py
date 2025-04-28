from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Nested schemas for related entities
class UserInfo(BaseModel):
    """
    Simplified user information schema for nested responses.
    Contains only essential user attributes for display in role contexts.
    """

    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessInfo(BaseModel):
    """
    Simplified process information schema for nested responses.
    Contains only the basic process attributes needed in role contexts.
    """

    id: int
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# Main schemas
class RoleBase(BaseModel):
    """
    Base schema for Role with common attributes.
    Defines the core field (title) shared by all role schemas.
    """

    title: str


class RoleCreate(RoleBase):
    """
    Schema for creating a new role.
    Extends the base schema with creator ID and optional process associations.
    """

    created_by_id: int
    process_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    """
    Schema for updating a role.
    All fields are optional to support partial updates of attributes
    and process relationships.
    """

    title: Optional[str] = None
    process_ids: Optional[List[int]] = []


class RoleRead(RoleBase):
    """
    Schema for reading role data.
    Provides a complete representation of a role including relationships
    with users and processes for API responses.
    """

    id: int
    created_by: Optional[UserInfo] = None
    processes: List[ProcessInfo] = []

    class Config:
        from_attributes = True
