# Docker Configuration

This project uses Docker for both development and production environments. Below is an explanation of the Docker-related files and their purposes.

## Docker Files

### Development Environment

- `Dockerfile`: Development container configuration

  - Based on Python 3.11 slim image
  - Includes development dependencies (gcc, postgresql-client)
  - Enables hot-reloading for development

- `docker-compose.yml`: Development environment setup
  - Runs the FastAPI application with debugger support
  - Sets up PostgreSQL database
  - Configures networking
  - Mounts source code as a volume for live updates
  - Includes health checks for database
  - Exposes ports:
    - 8000: FastAPI application
    - 7000: Debugger
    - 5432: PostgreSQL

### Production Environment

- `Dockerfile.prod`: Production container configuration
  - Multi-stage build for smaller image size
  - Separates build and runtime dependencies
  - Optimized for production use
  - No development tools included
  - Dev image size is 541MB and prod image size is 402MB(25.7% smaller)

### Testing Environment

- `docker-compose.test.yml`: Test environment setup
  - Separate PostgreSQL instance for testing
  - Isolated network for test environment
  - Uses the same base Dockerfile as development
  - Exposes ports:
    - 8000: Test API
    - 5432: Test PostgreSQL

## Environment Variables

### Development/Production

- `POSTGRES_SERVER`: Database host
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `POSTGRES_PORT`: Database port
- `ENV`: Environment type (development/production)

### Testing

- Same variables as above, but with test-specific values
- Database name: `test_db`
- Network: `test-app-network`

## Usage

### Development

```bash
# Start development environment
make up

# Access the application
http://localhost:8000
```

### Testing

```bash
# Run tests
make test
```

### Production

- Not required for now

## Volumes

- Development PostgreSQL data: `./postgres-data`
- Test PostgreSQL data: `./test-postgres-data`
- Application code: Mounted from host to `/app`

## Networks

- Development: `app-network`
- Testing: `test-app-network`

## Health Checks

PostgreSQL containers include health checks to ensure the database is ready before the application starts:

- Interval: 5 seconds
- Timeout: 5 seconds
- Retries: 5 (development) / 10 (testing)
