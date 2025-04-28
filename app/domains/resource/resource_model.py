from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for many-to-many relationship between Resource and Process
resource_process = Table(
    "resource_process",
    Base.metadata,
    Column("resource_id", Integer, ForeignKey("resources.id"), primary_key=True),
    Column("process_id", Integer, ForeignKey("process.id"), primary_key=True),
)


class Resource(Base):
    """
    Resource model representing assets or materials used in processes.

    A resource can be associated with multiple processes through a
    many-to-many relationship. Each resource tracks who created it and when.
    Resources might represent equipment, materials, or other items needed
    for business processes.
    """

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Foreign key to User who created this resource
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_resources", lazy="selectin")
    processes = relationship(
        "Process",
        secondary=resource_process,
        back_populates="resources",
        lazy="selectin",
    )
