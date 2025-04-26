from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """Base schema for User"""
    title: str


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    title: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user data"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 