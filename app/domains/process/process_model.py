from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Process(Base):
    """Process model"""
    
    __tablename__ = "process"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Foreign key to User who created this process
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship to User
    created_by = relationship("User", back_populates="created_processes")