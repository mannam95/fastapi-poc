from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import create_db_and_tables, create_initial_data, sessionmanager


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
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
