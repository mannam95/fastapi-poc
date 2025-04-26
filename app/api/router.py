from fastapi import APIRouter

from app.domains.process.process_router import router as process_router

api_router = APIRouter()

api_router.include_router(process_router, prefix="/processes", tags=["processes"])