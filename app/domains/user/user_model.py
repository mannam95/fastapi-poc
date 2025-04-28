from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User model representing system users who can create and manage entities.

    Users are the basic actors in the system and serve as creators for other entities
    (processes, departments, locations, resources, and roles). Each user has a title
    and creation timestamp. The relationships track all entities created by this user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships for created entities
    created_processes = relationship("Process", back_populates="created_by", lazy="selectin")
    created_departments = relationship("Department", back_populates="created_by", lazy="selectin")
    created_locations = relationship("Location", back_populates="created_by", lazy="selectin")
    created_resources = relationship("Resource", back_populates="created_by", lazy="selectin")
    created_roles = relationship("Role", back_populates="created_by", lazy="selectin")
