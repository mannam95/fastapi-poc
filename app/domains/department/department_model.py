from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for many-to-many relationship between Department and Process
department_process = Table(
    "department_process",
    Base.metadata,
    Column("department_id", Integer, ForeignKey("departments.id"), primary_key=True),
    Column("process_id", Integer, ForeignKey("process.id"), primary_key=True),
)


class Department(Base):
    """
    Department model representing an organizational department.

    A department can be associated with multiple processes through a
    many-to-many relationship. Each department tracks who created it and when.
    This model is used for organizing and categorizing processes by department.
    """

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Foreign key to User who created this department
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_departments", lazy="selectin")
    processes = relationship(
        "Process",
        secondary=department_process,
        back_populates="departments",
        lazy="selectin",
    )
