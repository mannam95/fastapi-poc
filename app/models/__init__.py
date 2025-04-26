# app/models/__init__.py
# This file exists to register all models in the app

from app.domains.process.process_model import Process

__all__ = ["Process"]