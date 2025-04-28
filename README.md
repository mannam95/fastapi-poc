# FastAPI with Async SQLAlchemy

A modern API application demonstrating FastAPI with async SQLAlchemy 2.0 and PostgreSQL.

## Features

- FastAPI with async SQLAlchemy 2.0
- PostgreSQL with asyncpg driver
- Migration support with Alembic
- Dependency injection pattern
- Docker Compose setup
- Comprehensive test suite

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose

## Quick Start

### With Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>

# Create environment file
# Not needed as this is POC, the necessary environment variables are already set in the docker-compose.yml file

# To start the application (See make help for all options)
make up

# Access API at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## Project Structure

```
app/
├── api/                # API router configuration
├── core/               # Core modules (config, database)
├── domains/            # Business domains
│   ├── department/     # Department domain
│   ├── location/       # Location domain
│   ├── process/        # Process domain
│   ├── resource/       # Resource domain
│   ├── role/           # Role domain
│   └── user/           # User domain
└── models/             # SQLAlchemy model imports
```

For detailed architecture and design decisions, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Common Tasks

### Database Migrations (TODO)

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Testing

```bash
# Run all tests
make test

# Run specific tests
make test-unit
make test-integration

# With coverage
make test-cov
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint
```

## Development Setup

### VSCode Setup

This project includes VSCode configuration files in the `.vscode` directory to provide a consistent development experience:

1. Install the recommended extensions when prompted by VSCode
2. Use the built-in debugger configurations:
   - Start the FastAPI server by running `make up` in the terminal
   - "Attach FastAPI Debugger": Can attach to a running FastAPI server

The configuration includes:

- Black formatter on save
- Flake8 and mypy linting
- additional settings for Python and FastAPI development

## Working with Async SQLAlchemy

### Using Database Sessions

```python
from app.core.database import DBSessionDep

@router.get("/items")
async def read_items(session: DBSessionDep):
    result = await session.execute(select(Item))
    items = result.scalars().all()
    return items
```

### Common Operations

```python
# Get item by ID
item = await session.get(Item, item_id)

# Query items
result = await session.execute(select(Item).where(Item.name == "test"))
items = result.scalars().all()

# Create item
item = Item(name="New Item")
session.add(item)
await session.commit()
await session.refresh(item)

# Update item
item = await session.get(Item, item_id)
item.name = "Updated Name"
await session.commit()

# Delete item
item = await session.get(Item, item_id)
await session.delete(item)
await session.commit()
```

For more detailed documentation, refer to the API docs at http://localhost:8000/docs when the application is running.
