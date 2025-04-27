# Testing Guide for FastAPI POC Project

This directory contains tests for the FastAPI Proof of Concept application. The tests are organized by domain and use pytest for test execution.

## Test Structure

The test directory structure mirrors the application structure:

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── utils.py                 # Utility functions for testing
├── domains/                 # Tests organized by domain
│   ├── process/             # Process domain tests
│   │   ├── test_process_service.py    # Process service tests
│   │   ├── test_process_router.py     # Process router tests
```

## Test Types

Tests are categorized using pytest markers:

- `unit`: Unit tests that test individual functions/methods
- `integration`: Integration tests that test interactions between components
- `service`: Tests for service layer logic
- `router`: Tests for API endpoints

## Running Tests

### Using Make Commands

The project's Makefile includes several commands to run tests:

```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov

# Run specific types of tests
make test-unit
make test-integration
make test-service
make test-router

# Run tests for specific domains
make test-process
```

### Using Pytest Directly

If you prefer to run pytest directly, you can use the following commands within the Docker environment:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Run tests by marker
pytest -m unit
pytest -m integration
pytest -m service
pytest -m router

# Run tests for a specific domain
pytest tests/domains/process/

# Run a specific test file
pytest tests/domains/process/test_process_service.py

# Run a specific test
pytest tests/domains/process/test_process_service.py::TestProcessService::test_create_process
```

## Adding New Tests

### Creating Tests for a New Domain

1. Create a new directory under `tests/domains/` for your domain
2. Add an `__init__.py` file to make it a Python package
3. Create test files for the service layer and router

Example:

```bash
mkdir -p tests/domains/new_domain
touch tests/domains/new_domain/__init__.py
touch tests/domains/new_domain/test_new_domain_service.py
touch tests/domains/new_domain/test_new_domain_router.py
```

### Testing Guidelines

1. **Test Independence**: Each test should be independent and not rely on the state created by other tests
2. **Use Fixtures**: Use pytest fixtures for shared setup and teardown
3. **Test Transactions**: Database tests use transaction rollback to prevent test data from persisting
4. **Test Coverage**: Aim for comprehensive test coverage, including success and error cases
5. **Asynchronous Testing**: Use the `@pytest.mark.asyncio` decorator for asynchronous tests
6. **Use Markers**: Apply appropriate markers to categorize your tests

## Test Database

Tests use a separate test database to avoid affecting development or production data. The test database is configured in `conftest.py` with the URL `postgresql+asyncpg://postgres:postgres@localhost:5432/test_db`.

Before running tests, make sure your PostgreSQL server is running and the test database exists:

```bash
createdb test_db
```

If you're using Docker, the test database will be created automatically when you run tests. 