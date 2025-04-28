from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    """
    Base schema for User with common attributes.
    Defines the core field (title) shared by all user schemas.
    """

    title: str


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Only requires the title field inherited from UserBase.
    """

    pass


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    All fields are optional to support partial updates.
    """

    title: Optional[str] = None


class UserRead(UserBase):
    """
    Schema for reading user data.
    Provides a complete representation of a user for API responses,
    including system-generated fields like ID and creation timestamp.
    """

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
