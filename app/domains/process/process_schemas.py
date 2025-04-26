from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class ProcessBase(BaseModel):
    title: str
    description: Optional[str] = None


class ProcessCreate(ProcessBase):
    department_ids: Optional[List[UUID]] = None
    role_ids: Optional[List[UUID]] = None
    resource_ids: Optional[List[UUID]] = None
    location_ids: Optional[List[UUID]] = None


class ProcessUpdate(ProcessBase):
    title: Optional[str] = None
    department_ids: Optional[List[UUID]] = None
    role_ids: Optional[List[UUID]] = None
    resource_ids: Optional[List[UUID]] = None
    location_ids: Optional[List[UUID]] = None


class ProcessInDBBase(ProcessBase):
    id: UUID
    created_at: datetime
    created_by_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class Process(ProcessInDBBase):
    """API response model"""
    pass


class ProcessDetail(Process):
    """Detailed process information including relations"""
