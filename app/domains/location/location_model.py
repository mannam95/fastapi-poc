from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for many-to-many relationship between Location and Process
location_process = Table(
    "location_process",
    Base.metadata,
    Column("location_id", Integer, ForeignKey("locations.id"), primary_key=True),
    Column("process_id", Integer, ForeignKey("process.id"), primary_key=True),
)


class Location(Base):
    """
    Location model representing physical or virtual places for processes.

    A location can be associated with multiple processes through a
    many-to-many relationship. Each location tracks who created it and when.
    Locations could represent physical facilities, virtual environments,
    or other spaces where business processes occur.
    """

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Foreign key to User who created this location
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_locations", lazy="selectin")
    processes = relationship(
        "Process",
        secondary=location_process,
        back_populates="locations",
        lazy="selectin",
    )
