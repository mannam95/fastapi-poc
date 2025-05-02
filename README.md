# FastAPI with Async SQLAlchemy

A modern API application demonstrating FastAPI with async SQLAlchemy 2.0 and PostgreSQL.

## Features

- FastAPI with async SQLAlchemy 2.0
- PostgreSQL with asyncpg driver
- Domain-Driven Design (DDD)
- Dependency injection pattern
- Centralized logging with Loguru
- Centralized Exception handling
- Docker Compose setup
- Comprehensive test suite
- Benchmarking with Locust
- Code formatting with Black and isort
- Code linting with Flake8
- Type checking with Mypy

# TODO items

- Prometheus and Grafana for monitoring
- Migration support with Alembic
- Redis for caching
- WebSockets
  - support is there just that I couldn't find time to implement it.

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose

## Quick Start

### With Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>

# Start the application
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

docker/
├── Dockerfile          # Dockerfile for development
├── Dockerfile.prod     # Dockerfile for production
└── docker-compose.yml  # Docker Compose configuration

tests/
├── conftest.py         # Pytest configuration
├── domains/            # Test domains
│   ├── department/     # Department test cases
│   ├── location/       # Location test cases
│   ├── process/        # Process test cases
│   ├── resource/       # Resource test cases
│   ├── role/           # Role test cases
│   └── user/           # User test cases
└── test_models.py      # Model test cases

sql-scripts/
├── init.sql         # Initial SQL script
```

## Documentation

For detailed documentation, please refer to the following files in the `docs` directory:

- [Architecture & Design Decisions](docs/01-architecture.md)
- [Working with Async SQLAlchemy](docs/02-sqlalchemy.md)
- [Docker Configuration](docs/03-docker.md)
- [Testing Guide](docs/04-testing.md)
- [Formatting & Linting](docs/05-formatting.md)
- [Benchmarking](docs/06-benchmarking.md)
- [Python virtual environment](docs/07-venv.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
