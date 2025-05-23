"""
Main API router module that aggregates all domain-specific routers.
This module centralizes routing configuration for the entire API.
"""

from fastapi import APIRouter

from app.domains.department.department_router import router as department_router
from app.domains.location.location_router import router as location_router
from app.domains.process.process_router import router as process_router
from app.domains.resource.resource_router import router as resource_router
from app.domains.role.role_router import router as role_router
from app.domains.user.user_router import router as user_router

api_router = APIRouter()

api_router.include_router(process_router, prefix="/processes", tags=["processes"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(department_router, prefix="/departments", tags=["departments"])
api_router.include_router(location_router, prefix="/locations", tags=["locations"])
api_router.include_router(resource_router, prefix="/resources", tags=["resources"])
api_router.include_router(role_router, prefix="/roles", tags=["roles"])
