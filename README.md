# FastAPI with Async SQLAlchemy

This is a FastAPI Proof of Concept project demonstrating the use of async SQLAlchemy 2.0 with PostgreSQL.

## Features

- FastAPI with async SQLAlchemy 2.0
- PostgreSQL with asyncpg driver
- Migration support with Alembic
- Dependency injection pattern for database sessions
- Docker Compose setup for development
- Comprehensive test suite with pytest

## Requirements

- Python 3.10+
- PostgreSQL 14+
- Docker and Docker Compose (optional)

## Getting Started

### Environment Setup

1. Create a `.env` file from the template:

```bash
cp .env.example .env
```

2. Edit the `.env` file to set your PostgreSQL connection details:

```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_poc
POSTGRES_PORT=5432
```

### Running with Docker

The simplest way to get started is using Docker Compose:

```bash
docker-compose up -d
```

This will start the FastAPI application and a PostgreSQL database.

### Running Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
uvicorn app.main:app --reload
```

## Testing

The project includes a comprehensive test suite using pytest. Tests are organized by domain and type.

### Running Tests

To run tests using Docker:

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test types
make test-unit
make test-integration
make test-service
make test-router

# Run tests for specific domains
make test-process
```

To run tests locally:

```bash
# Create a test database
createdb test_db

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

For more information about testing, see the [Testing Guide](tests/README.md).

## Project Structure

```
app/
├── alembic/                # Database migrations
├── api/                    # API router and endpoints
├── core/                   # Application core modules
│   ├── config.py           # Application configuration
│   ├── database.py         # Async SQLAlchemy setup
├── domains/                # Business domains
│   ├── process/            # Process domain
│   │   ├── process_model.py    # SQLAlchemy models
│   │   ├── process_router.py   # FastAPI routers
│   │   ├── process_schemas.py  # Pydantic schemas
│   │   ├── process_service.py  # Business logic
├── models/                 # SQLAlchemy models (imports)
tests/
├── conftest.py             # Test fixtures and configuration
├── domains/                # Tests organized by domain
│   ├── process/            # Process domain tests
```

## Working with Async SQLAlchemy

### Database Session

The database session is managed by the `DatabaseSessionManager` class in `app/core/database.py`. It provides a session factory that creates an async SQLAlchemy session.

To use the database session in your endpoints, use the `DBSessionDep` dependency:

```python
from app.core.database import DBSessionDep

@router.get("/items")
async def read_items(session: DBSessionDep):
    # Use the session here
    result = await session.execute(select(Item))
    items = result.scalars().all()
    return items
```

### Creating Models

Create your SQLAlchemy models using the `Base` class from `app/core/database.py`:

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
```

### Common Async SQLAlchemy Operations

#### Querying Data

```python
# Get a single item by primary key
item = await session.get(Item, item_id)

# Select multiple items
result = await session.execute(select(Item).where(Item.name == "test"))
items = result.scalars().all()
```

#### Creating Data

```python
# Create a new item
item = Item(name="New Item", description="Description")
session.add(item)
await session.commit()
await session.refresh(item)  # To get the generated ID and other DB-computed values
```

#### Updating Data

```python
# Update an item
item = await session.get(Item, item_id)
item.name = "Updated Name"
await session.commit()
```

#### Deleting Data

```python
# Delete an item
item = await session.get(Item, item_id)
await session.delete(item)
await session.commit()
```

## Error Handling

When working with async SQLAlchemy, always use try/except blocks and handle session rollbacks:

```python
try:
    # Database operations
    await session.commit()
except Exception as e:
    await session.rollback()
    # Handle the error
```

## Database Migrations

This project uses Alembic for database migrations. To create a new migration:

```bash
alembic revision --autogenerate -m "Description of the migration"
```

To apply migrations:

```bash
alembic upgrade head
```

## API Documentation

When the application is running, you can access the automatic API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc