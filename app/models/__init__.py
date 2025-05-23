# app/models/__init__.py
# This file exists to register all models in the app

from app.domains.department.department_model import Department
from app.domains.location.location_model import Location

# Import all models to ensure they are registered with SQLAlchemy Base
from app.domains.process.process_model import Process
from app.domains.resource.resource_model import Resource
from app.domains.role.role_model import Role
from app.domains.user.user_model import User

__all__ = ["Process", "User", "Department", "Location", "Resource", "Role"]
