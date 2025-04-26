from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships for created entities
    created_processes = relationship("Process", back_populates="created_by")