from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Process(Base):
    """
    Process model representing a business process in the system.

    A process can be associated with multiple departments, locations,
    resources, and roles through many-to-many relationships.
    Each process tracks who created it and when.
    """

    __tablename__ = "process"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    # Foreign key to User who created this process
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to User
    created_by = relationship("User", back_populates="created_processes", lazy="selectin")

    # Many-to-many relationships
    departments = relationship(
        "Department",
        secondary="department_process",
        back_populates="processes",
        lazy="selectin",
    )
    locations = relationship(
        "Location",
        secondary="location_process",
        back_populates="processes",
        lazy="selectin",
    )
    resources = relationship(
        "Resource",
        secondary="resource_process",
        back_populates="processes",
        lazy="selectin",
    )
    roles = relationship(
        "Role", secondary="role_process", back_populates="processes", lazy="selectin"
    )
