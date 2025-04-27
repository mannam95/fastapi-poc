from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Process(Base):
    """Process model"""
    
    __tablename__ = "process"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    # Foreign key to User who created this process
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship to User
    created_by = relationship("User", back_populates="created_processes", lazy="selectin")
    
    # Many-to-many relationships
    departments = relationship("Department", secondary="department_process", back_populates="processes", lazy="selectin")
    locations = relationship("Location", secondary="location_process", back_populates="processes", lazy="selectin")
    resources = relationship("Resource", secondary="resource_process", back_populates="processes", lazy="selectin")
    roles = relationship("Role", secondary="role_process", back_populates="processes", lazy="selectin")