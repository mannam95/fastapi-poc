from fastapi import APIRouter

from app.domains.process.process_router import router as process_router
from app.domains.user.user_router import router as user_router

api_router = APIRouter()

api_router.include_router(process_router, prefix="/processes", tags=["processes"])
api_router.include_router(user_router, prefix="/users", tags=["users"])