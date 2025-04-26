# app/models/__init__.py
# This file exists to register all models in the app

# Import all models to ensure they are registered with SQLAlchemy Base
from app.domains.process.process_model import Process
from app.domains.user.user_model import User
from app.domains.department.department_model import Department

__all__ = [
    "Process", 
    "User", 
    "Department"
]