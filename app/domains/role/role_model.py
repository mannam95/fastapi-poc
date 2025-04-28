from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for many-to-many relationship between Role and Process
role_process = Table(
    "role_process",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("process_id", Integer, ForeignKey("process.id"), primary_key=True),
)


class Role(Base):
    """
    Role model representing job functions or responsibilities.

    A role can be associated with multiple processes through a
    many-to-many relationship. Each role tracks who created it and when.
    Roles represent job positions, responsibilities, or functions that
    are involved in executing business processes.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Foreign key to User who created this role
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_roles", lazy="selectin")
    processes = relationship(
        "Process", secondary=role_process, back_populates="roles", lazy="selectin"
    )
