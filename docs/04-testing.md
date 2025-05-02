# Testing Guide

This guide covers the testing approach for the FastAPI project.

## Test Structure

```
tests/
├── conftest.py            # Pytest fixtures and configuration
├── domains/               # Tests organized by domain
│   ├── department/
│   ├── location/
│   ├── process/
│   ├── resource/
│   ├── role/
│   └── user/
```

## Running Tests

```bash
# All tests
make test

# Specific test types
make test-unit # TODO: Add unit tests
make test-integration # Currently only integration tests are implemented

# Coverage report
make test-cov
```

## Test Database

Tests use a separate database. With Docker, the test database is created automatically.
For local development, you may need to create a test database:

```bash
createdb test_fastapi_poc
```

## Writing New Tests

1. Place tests in the appropriate domain directory
2. Use fixtures from conftest.py for database and client setup
3. Use appropriate markers (`unit`, `integration`)
4. Test both success and error cases
5. Test database operations use transaction rollbacks

## Example Test

```python
@pytest.mark.integration
async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/users/",
        json={"name": "Test User", "email": "test@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
```
