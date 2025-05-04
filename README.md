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

### Makefile

- A simple Makefile is provided and multiple commands are available.
- You can check the Makefile for more details or `make help` to see the available commands.

### With Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>

# Start the application (includes database initialization)
make up

# Access API at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Any Issues?

- Any issues faced, just use below command to `nuke` the environment and start again.

```bash
make nuke
```

## Documentation

For detailed documentation, please refer to the following files in the `docs` directory:

- [Architecture & Design Decisions](docs/00-architecture.md)
- [Programming Practices](docs/01-code_style.md)
- [Working with Async SQLAlchemy](docs/02-sqlalchemy.md)
- [Docker Configuration](docs/03-docker.md)
- [Testing Guide](docs/04-testing.md)
- [Formatting & Linting](docs/05-formatting.md)
- [Benchmarking](docs/06-benchmarking.md)
- [Python virtual environment](docs/07-venv.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
