from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Association table for many-to-many relationship between Location and Process
location_process = Table(
    "location_process",
    Base.metadata,
    Column("location_id", Integer, ForeignKey("locations.id"), primary_key=True),
    Column("process_id", Integer, ForeignKey("process.id"), primary_key=True)
)

class Location(Base):
    """Location model"""
    
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Foreign key to User who created this location
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    created_by = relationship("User", back_populates="created_locations", lazy="selectin")
    processes = relationship("Process", secondary=location_process, back_populates="locations", lazy="selectin") 