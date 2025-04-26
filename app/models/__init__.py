# app/models/__init__.py
# This file exists to register all models in the app

from app.domains.process.process_model import Process
from app.domains.user.user_model import User

__all__ = ["Process", "User"]