from pydantic import BaseModel

class ProcessCreate(BaseModel):
    title: str
    description: str | None = None
    
    class Config:
        from_attributes = True

class ProcessRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    
    class Config:
        from_attributes = True

class ProcessUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    
    class Config:
        from_attributes = True
