from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware import Middleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import create_db_and_tables, create_initial_data, sessionmanager
from app.core.exceptions import AppException
from app.core.logging_middleware import LoggingMiddleware
from app.core.logging_service import get_logging_service

# Add logging middleware
middleware = [Middleware(LoggingMiddleware, logging_service=get_logging_service())]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    # Initialize the database connection
    db_url = settings.SQLALCHEMY_DATABASE_URI
    sessionmanager.init(db_url)

    # Create database tables
    await create_db_and_tables()
    await create_initial_data()

    yield

    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Proof of Concept",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": 0, "docExpansion": None},
    lifespan=lifespan,
    middleware=middleware,
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Global handler for custom application exceptions"""
    await get_logging_service().log_api_exception(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    """
    Endpoint for monitoring health status of the application.
    Returns a simple status message indicating the API is operational.
    """
    return {"status": "ok"}
