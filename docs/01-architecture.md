# Architecture & Design Decisions

This document outlines the architecture and key design decisions for the FastAPI project.

## Project Structure

```
/
├── alembic/              # Database migration scripts
├── app/
│   ├── api/              # API router configuration
│   │   └── api.py        # Main API router
│   ├── core/             # Core application components
│   │   ├── config.py     # Application configuration
│   │   └── database.py   # Database setup and dependencies
│   ├── domains/          # Business domains (DDD approach)
│   │   ├── department/   # Department domain
│   │   ├── location/     # Location domain
│   │   ├── process/      # Process domain
│   │   ├── resource/     # Resource domain
│   │   ├── role/         # Role domain
│   │   ├── shared/       # Shared domain components
│   │   └── user/         # User domain
│   ├── models/           # SQLAlchemy model imports
│   └── main.py           # Application entry point
├── migrations/           # Alembic migration configuration
├── tests/                # Test suite
│   ├── conftest.py       # Test fixtures
│   └── domains/          # Tests organized by domain
└── docker/               # Docker configuration files
```

## Design Decisions

### 1. Domain-Driven Design (DDD)

We've adopted a Domain-Driven Design approach, organizing code by business domains rather than technical layers. This helps:

- **Maintain bounded contexts**: Each domain has its own models, schemas, and logic
- **Scale the codebase**: Teams can work on separate domains with minimal conflicts
- **Business alignment**: Code structure reflects business concepts

### 2. Async-First Architecture

The application uses async/await throughout:

- **FastAPI**: Native async support for request handling
- **SQLAlchemy 2.0**: Async ORM with the new 2.0-style queries
- **Asyncpg**: High-performance async PostgreSQL driver

This provides better resource utilization and scalability, especially for I/O-bound operations.

### 3. Service-Based Data Access

The application uses SQLAlchemy directly in the service layer:

- **Direct ORM usage**: Services directly use SQLAlchemy for data access
- **No repository abstraction**: SQLAlchemy itself provides the data access abstraction
- **Session management**: Database sessions are managed through FastAPI's dependency injection

This approach simplifies the architecture by leveraging SQLAlchemy's powerful query capabilities without adding an additional repository layer.

### 4. Dependency Injection

FastAPI's dependency injection system is used extensively:

- **Database sessions**: Automatically managed through dependencies
- **Service injection**: Domain services are injected into routes
- **Repository injection**: Repositories are injected into services

This creates a clean separation between components and simplifies testing.

### 5. Schemas vs Models

We maintain a clear distinction:

- **SQLAlchemy Models**: Define database structure
- **Pydantic Schemas**: Define API contracts (request/response)

This separation prevents leaking database implementation details to API consumers.

### 6. Migration Strategy

Alembic is used for database migrations:

- **Version control**: Database schema changes are tracked
- **Automated migration**: Schema changes can be generated from model changes
- **Rollback support**: Migrations can be reversed if needed

### 7. Containerization

Docker is used for development and deployment:

- **Consistent environments**: Same environment for all developers
- **Dependency isolation**: Services run in isolated containers
- **Simple orchestration**: Docker Compose for local development
- **Image size**: The production image is built with a multi-stage build to reduce the size of the final image.

## Key Technologies

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy 2.0**: SQL toolkit and ORM with async support
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migration tool
- **Pytest**: Testing framework
- **PostgreSQL**: Relational database
- **Docker**: Containerization
