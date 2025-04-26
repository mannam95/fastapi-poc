from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Nested schema for simplified user info
class UserInfo(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProcessCreate(BaseModel):
    title: str
    description: Optional[str] = None
    created_by_id: int
    
    class Config:
        from_attributes = True

class ProcessRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_by_id: int
    created_by: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True

class ProcessUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
