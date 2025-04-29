from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """
    User model representing system users who can create and manage entities.

    Users are the basic actors in the system and serve as creators for other entities
    (processes, departments, locations, resources, and roles). Each user has a title
    and creation timestamp. The relationships track all entities created by this user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships for created entities
    created_processes = relationship("Process", back_populates="created_by", lazy="selectin")
    created_departments = relationship("Department", back_populates="created_by", lazy="selectin")
    created_locations = relationship("Location", back_populates="created_by", lazy="selectin")
    created_resources = relationship("Resource", back_populates="created_by", lazy="selectin")
    created_roles = relationship("Role", back_populates="created_by", lazy="selectin")
